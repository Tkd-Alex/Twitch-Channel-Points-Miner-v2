import os
import pickle
from exceptions import WrongCookiesException


# Name of the file where cookies will be saved. It will be located in the folder with the sources.
COOKIES_FILENAME = "twitch-cookies.pkl"


def get_cookie_value(key):
    cookies = load_cookies()
    for cookie in cookies:
        if cookie["name"] == key:
            if cookie["value"] is not None:
                return cookie["value"]
    # delete current cookie file as it's invalid
    os.remove(get_cookies_path())
    raise WrongCookiesException(f"Can't find cookie for key {key}, must login again!")


cookies_cached = None


def load_cookies():
    global cookies_cached
    cookie_path = get_cookies_path()
    if cookies_cached is None:
        if os.path.isfile(cookie_path):
            cookies_cached = pickle.load(open(cookie_path, "rb"))
        else:
            raise WrongCookiesException("There must be a cookies file!")

    return cookies_cached


def save_cookies_to_file(cookies_dict):
    cookies = []
    for cookie_name, value in cookies_dict.items():
        cookies.append({"name": cookie_name, "value": value})
    pickle.dump(cookies, open(get_cookies_path(), "wb"))


def get_cookies_path():
    # find a file called COOKIES_FILENAME in the same directory where the source files are
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), COOKIES_FILENAME)