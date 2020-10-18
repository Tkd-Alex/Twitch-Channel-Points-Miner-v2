import getpass
import os
import browser_cookie3
import requests
from cookies import get_cookies_path, save_cookies_to_file
from twitch_data import get_client_id


# Based on https://github.com/derrod/twl.py
# Original Copyright (c) 2020 Rodney
# The MIT License (MIT)


def check_login():
    if not os.path.exists(get_cookies_path()):
        twitch_login = TwitchLogin()
        success = twitch_login.login_flow()
        if success:
            twitch_login.save_cookies()
            print("Login successful!")
        return success
    else:
        return True


class TwitchLogin:
    def __init__(self):
        self.token = None
        self.login_check_result = False
        self.session = requests.session()
        self.session.headers.update({'Client-ID': get_client_id()})
        self.username = None
        self.user_id = None
        self.email = None

    def login_flow(self):
        print("You'll have to login to Twitch!")

        post_data = {
            'client_id': get_client_id(),
            'undelete_user': False,
            'remember_me': True
        }

        use_backup_flow = False

        while True:
            self.username = input('Enter Twitch username: ')
            password = getpass.getpass('Enter Twitch password: ')

            post_data['username'] = self.username
            post_data['password'] = password

            while True:
                # Try login without 2FA
                login_response = self.send_login_request(post_data)

                if 'captcha_proof' in login_response:
                    post_data['captcha'] = dict(proof=login_response['captcha_proof'])

                if 'error_code' in login_response:
                    err_code = login_response['error_code']
                    if err_code == 3011 or err_code == 3012:  # missing 2fa token
                        if err_code == 3011:
                            print('Two factor authentication enabled, please enter token below.')
                        else:
                            print('Invalid two factor token, please try again.')

                        twofa = input('2FA token: ')
                        post_data['authy_token'] = twofa.strip()
                        continue

                    elif err_code == 3022 or err_code == 3023:  # missing 2fa token
                        if err_code == 3022:
                            print('Login Verification code required.')
                            self.email = login_response['obscured_email']
                        else:
                            print('Invalid Login Verification code entered, please try again.')

                        twofa = input(f'Please enter the 6-digit code sent to {self.email}: ')
                        post_data['twitchguard_code'] = twofa.strip()
                        continue

                    elif err_code == 3001:  # invalid password
                        print('Invalid username or password, please try again.')
                        break
                    elif err_code == 1000:
                        print('Console login unavailable (CAPTCHA solving required).')
                        use_backup_flow = True
                        break
                    else:
                        print(f'Unknown error: {login_response}')
                        raise NotImplementedError(f'Unknown TwitchAPI error code: {err_code}')

                if 'access_token' in login_response:
                    self.set_token(login_response['access_token'])
                    return self.check_login()

            if use_backup_flow:
                break

        if use_backup_flow:
            self.set_token(self.login_flow_backup())
            return self.check_login()

        return False

    def set_token(self, new_token):
        self.token = new_token
        self.session.headers.update({'Authorization': f'Bearer {self.token}'})

    def send_login_request(self, json_data):
        r = self.session.post('https://passport.twitch.tv/login', json=json_data)
        j = r.json()
        return j

    def login_flow_backup(self):
        """Backup OAuth login flow in case manual captcha solving is required"""
        browser = input("What browser do you use? Chrome (1), Firefox (2), Other (3): ").strip()
        if browser not in ("1", "2"):
            print("Your browser is unsupported, sorry.")
            return None

        input("Please login inside your browser of choice (NOT incognito mode) and press Enter...")
        print("Loading cookies saved on your computer...")
        twitch_domain = ".twitch.tv"
        if browser == "1":  # chrome
            cookie_jar = browser_cookie3.chrome(domain_name=twitch_domain)
        else:
            cookie_jar = browser_cookie3.firefox(domain_name=twitch_domain)
        cookies_dict = requests.utils.dict_from_cookiejar(cookie_jar)
        self.username = cookies_dict.get("login")
        return cookies_dict.get("auth-token")

    def check_login(self):
        if self.login_check_result:
            return self.login_check_result
        if self.token is None:
            return False

        r = self.session.get(f'https://api.twitch.tv/helix/users?login={self.username}')
        response = r.json()
        if "data" in response:
            self.login_check_result = True
            self.user_id = response["data"][0]["id"]

        return self.login_check_result

    def save_cookies(self):
        cookies_dict = self.session.cookies.get_dict()
        cookies_dict["auth-token"] = self.token
        if "persistent" not in cookies_dict:  # saving user id cookies
            cookies_dict["persistent"] = self.user_id
        save_cookies_to_file(cookies_dict)
