from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging
from time import sleep
import re
import pickle
import os
import traceback
from hidden_chrome_driver import HiddenChromeWebDriver


PAGE_LOAD_WAIT_SECONDS = 3
COOKIES_FILENAME = "./twitch-cookies.pkl"


def main():
    global twitch_streamer
    twitch_streamer = input("Enter the streamer name: ")
    print("Loading, please wait...")
    create_webdriver(True)
    check_login()
    
    if not streamer_exists():
        print("This streamer does not exist.")
        driver.quit()
        return
    
    check_mature_content()
    
    try:
        set_lowest_quality()
        go_fullscreen()
        while True:
            check_for_credits_update()
            check_for_bonus()
            sleep(5)
    except:
        print("The streamer is offline currently.")
        driver.quit()
        return
      


def create_webdriver(headless):
    global driver
    
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1280,800");
        #chrome_options.add_argument("--disable-gpu")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument("--mute-audio")

    
    driver = HiddenChromeWebDriver(service_log_path='NUL', options=chrome_options)    
    if headless:
        url = f"https://www.twitch.com/{twitch_streamer}"
    else:
        url = "https://www.twitch.com"
    driver.get(url)
    load_cookies()
    sleep(PAGE_LOAD_WAIT_SECONDS)
    return driver


def save_cookies():
    pickle.dump(driver.get_cookies(), open(COOKIES_FILENAME, "wb"))


def load_cookies():
    if os.path.isfile(COOKIES_FILENAME):
        cookies = pickle.load(open(COOKIES_FILENAME, "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)

        driver.refresh()

    

def check_login():
    while True:
        login_button_search = driver.find_elements_by_css_selector("button[data-a-target='login-button']")
        if len(login_button_search) > 0:
            print("You'll have to login to Twitch, please wait.")
            driver.quit()
            create_webdriver(False)
            input("Please login to Twitch and press Enter when you're done...")
            save_cookies()
            driver.quit()
            print("Loading, please wait...")
            create_webdriver(True)
        else:
            break


def streamer_exists():
    error_search = driver.find_elements_by_css_selector("a[data-test-selector='page-not-found__browse-channels-button']")
    return len(error_search) == 0


def check_mature_content():
    accept_button_search = driver.find_elements_by_css_selector("button[data-a-target='player-overlay-mature-accept']")
    if accept_button_search:
        accept_button = accept_button_search[0]
        accept_button.click()
        sleep(1)

    
def set_lowest_quality():
    settings_button = driver.find_element_by_css_selector("button[data-a-target='player-settings-button']")
    settings_button.click()
    sleep(0.1)
    quality_button = driver.find_element_by_css_selector("button[data-a-target='player-settings-menu-item-quality']")
    quality_button.click()

    qualities = driver.find_elements_by_css_selector("div[data-a-target='player-settings-submenu-quality-option']")
    qualities[-1].click()


def go_fullscreen():
    fullscreen_button = driver.find_element_by_css_selector("button[data-a-target='player-fullscreen-button']")
    fullscreen_button.click()    


def check_for_bonus():
    bonus_button_search = driver.find_elements_by_css_selector("button[class='tw-button tw-button--success tw-interactive']")
    if bonus_button_search:
        bonus_button = bonus_button_search[0]
        bonus_button.click()
        print("Clicked the bonus button!")


current_credits = -1

def check_for_credits_update():
    global current_credits
    new_credits = get_credits()
    if new_credits != current_credits:
        current_credits = new_credits
        print(f"Now you have {current_credits} credits!")


def get_credits():
    balance_div = driver.find_element_by_css_selector("div[data-test-selector='balance-string']")
    balance_text_span = balance_div.find_element_by_class_name("tw-animated-number")
    balance_text = balance_text_span.text
    # убираем пробелы
    balance_text = re.sub(r"\s+", "", balance_text, flags=re.UNICODE)
    if len(balance_text) == 0:
        return -1
    else:
        return int(balance_text)


if __name__ == "__main__":
    main()

