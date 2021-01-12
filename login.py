import os
from cookies import get_cookies_path
from classes.TwitchLogin import TwitchLogin

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


