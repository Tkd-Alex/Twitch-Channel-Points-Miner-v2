import atexit
import os
import pickle
import re
import time
from selenium.common.exceptions import *
from selenium.webdriver.chrome.options import Options
from hidden_chrome_driver import HiddenChromeWebDriver

PAGE_LOAD_WAIT_SECONDS = 3
COOKIES_FILENAME = "./twitch-cookies.pkl"

driver: HiddenChromeWebDriver
is_fullscreen = False
twitch_streamer: str
is_online = None
current_channel_points = -1


def main():
    global twitch_streamer
    twitch_streamer = input("Enter the streamer name: ")
    print("Loading, please wait...")
    create_webdriver(True)
    check_login()

    if not streamer_exists():
        print("This streamer does not exist.")
        return

    while True:
        try:
            start_watching_stream()
        except (NoSuchElementException, StaleElementReferenceException):
            set_online(False)
        except RaidRedirectException:
            pass
        sleep(90)


def start_watching_stream():
    load_url(get_streamer_url())

    check_mature_content()
    set_lowest_quality()
    if not is_fullscreen:
        toggle_fullscreen()

    get_channel_points()  # throws NoSuchElementException when streamer is offline
    set_online(True)

    while True:
        check_for_raid_redirect()
        check_for_channel_points_update()
        check_for_bonus()
        sleep(5)


def create_webdriver(headless):
    global driver, is_fullscreen

    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1280,800")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument("--mute-audio")

    driver = HiddenChromeWebDriver(options=chrome_options, service_log_path='NUL' if os.name == "nt" else "/dev/null")
    if headless:
        url = get_streamer_url()
    else:
        url = "https://www.twitch.tv"
    driver.get(url)
    is_fullscreen = False
    load_cookies()
    sleep(PAGE_LOAD_WAIT_SECONDS)
    return driver


def load_url(url):
    global is_fullscreen
    if driver.current_url != url:
        driver.get(url)
        is_fullscreen = False
        sleep(PAGE_LOAD_WAIT_SECONDS)


def get_streamer_url():
    return f"https://www.twitch.tv/{twitch_streamer}"


def check_login():
    while True:
        login_button_search = driver.find_elements_by_css_selector("button[data-a-target='login-button']")
        if len(login_button_search) > 0:
            print("You'll have to login to Twitch, please wait.")
            quit_driver()
            create_webdriver(False)
            input("Please login to Twitch and press Enter when you're done...")
            save_cookies()
            quit_driver()
            print("Loading, please wait...")
            create_webdriver(True)
        else:
            break


def save_cookies():
    pickle.dump(driver.get_cookies(), open(COOKIES_FILENAME, "wb"))


def load_cookies():
    if os.path.isfile(COOKIES_FILENAME):
        cookies = pickle.load(open(COOKIES_FILENAME, "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)

        driver.refresh()


def streamer_exists():
    error_search = driver.find_elements_by_css_selector(
        "a[data-test-selector='page-not-found__browse-channels-button']")
    return len(error_search) == 0


def check_mature_content():
    accept_button_search = driver.find_elements_by_css_selector("button[data-a-target='player-overlay-mature-accept']")
    if accept_button_search:
        accept_button = accept_button_search[0]
        accept_button.click()
        sleep(1)


def set_lowest_quality():
    close_discount_balloon()

    settings_button = driver.find_element_by_css_selector("button[data-a-target='player-settings-button']")
    settings_button.click()
    sleep(0.1)
    quality_button = driver.find_element_by_css_selector("button[data-a-target='player-settings-menu-item-quality']")
    quality_button.click()

    qualities = driver.find_elements_by_css_selector("div[data-a-target='player-settings-submenu-quality-option']")
    qualities[-1].click()


# Sometimes Twitch will show a SUBtember discount, which will overlay the settings button
def close_discount_balloon():
    close_button_div_search = driver.find_elements_by_css_selector(
        "div[class='tw-absolute tw-pd-1 tw-right-0 tw-top-0']")
    if close_button_div_search:
        close_button = close_button_div_search[0].find_element_by_css_selector("button")
        close_button.click()


def toggle_fullscreen():
    global is_fullscreen
    fullscreen_button = driver.find_element_by_css_selector("button[data-a-target='player-fullscreen-button']")
    fullscreen_button.click()
    is_fullscreen = not is_fullscreen


def set_online(new_online):
    global is_online
    if is_online != new_online:
        is_online = new_online
        if is_online:
            print("The streamer is live!")
        else:
            print("The streamer is offline currently.")
            print("Wait for him to go live, or close the program by pressing Ctrl+C.")

    if not is_online:
        load_url("about:blank")


def check_for_raid_redirect():
    if driver.current_url != get_streamer_url():
        print("You have followed the raid!")
        sleep(30)  # pretend we're following the raid
        driver.get(get_streamer_url())
        raise RaidRedirectException


class RaidRedirectException(Exception):
    pass


def check_for_bonus():
    bonus_button_search = driver.find_elements_by_css_selector(
        "button[class='tw-button tw-button--success tw-interactive']")
    if bonus_button_search:
        bonus_button = bonus_button_search[0]
        bonus_button.click()
        print("Clicked the bonus button!")


def check_for_channel_points_update():
    global current_channel_points
    new_channel_points = get_channel_points()
    if new_channel_points != current_channel_points:
        current_channel_points = new_channel_points
        print(f"Now you have {current_channel_points} channel points!")


def get_channel_points():
    balance_div = driver.find_element_by_css_selector("div[data-test-selector='balance-string']")
    balance_text_span = balance_div.find_element_by_class_name("tw-animated-number")
    balance_text = balance_text_span.text
    # remove spaces
    balance_text = re.sub(r"\s+", "", balance_text, flags=re.UNICODE)
    if len(balance_text) == 0:
        raise NoSuchElementException
    else:
        return int(balance_text)


def quit_driver():
    global driver
    driver.quit()
    driver.service.stop()
    del driver


@atexit.register
def exit_handler():
    if "driver" in globals():
        print("Closing the webdriver...")
        quit_driver()
        if os.name == "nt":
            print("Because of a bug in chromedriver, there are still chrome.exe processes occupying the memory.")
            should_kill_chrome = input("Kill them? This will close ALL of Chrome instances! y/n: ")
            if should_kill_chrome.lower() == "y":
                os.system("taskkill /im chrome.exe /f")


def sleep(t):  # workaround so that sleep doesn't block keyboard interrupt
    while t >= 1:
        time.sleep(1)
        t -= 1
    time.sleep(t)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit_handler()
