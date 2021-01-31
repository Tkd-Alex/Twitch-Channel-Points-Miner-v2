import logging
import os
import platform
import random
import time

from enum import Enum, auto
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import JavascriptException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from TwitchChannelPointsMiner.classes.EventPrediction import EventPrediction
from TwitchChannelPointsMiner.constants.browser import Javascript, Selectors
from TwitchChannelPointsMiner.constants.twitch import URL
from TwitchChannelPointsMiner.utils import bet_condition, get_user_agent
from TwitchChannelPointsMiner.utils import millify

logger = logging.getLogger(__name__)


class Browser(Enum):
    CHROME = auto()
    FIREFOX = auto()


class BrowserSettings:
    def __init__(
        self,
        timeout: float = 10.0,
        implicitly_wait: int = 5,
        max_attempts: int = 3,
        do_screenshot: bool = False,  # Options for debug
        save_html: bool = False,  # Options for debug
        show: bool = True,
        browser: Browser = Browser.FIREFOX,
        driver_path: str = None,
    ):
        self.timeout = timeout
        self.implicitly_wait = implicitly_wait
        self.max_attempts = max_attempts
        self.do_screenshot = do_screenshot
        self.save_html = save_html
        self.show = show
        self.browser = browser
        self.driver_path = (
            driver_path
            if driver_path is not None
            else os.path.join(
                Path().absolute(),
                (
                    ("chromedriver" if browser == Browser.CHROME else "geckodriver")
                    + (".exe" if platform.system() == "Windows" else "")
                ),
            )
        )


class TwitchBrowser:
    def __init__(
        self,
        auth_token: str,
        session_id: str,
        settings: BrowserSettings,
    ):
        self.auth_token = auth_token
        self.session_id = session_id
        self.settings = settings

        self.currently_is_betting = False
        self.browser = None

    def init(self):
        if self.settings.browser == Browser.FIREFOX:
            self.__init_firefox()
        elif self.settings.browser == Browser.CHROME:
            self.__init_chrome()

        if self.browser is not None:
            self.browser.set_window_size(450, 800)
            self.browser.implicitly_wait(self.settings.implicitly_wait)

        self.__init_twitch()

    def __init_twitch(self):
        logger.debug(
            "Init Twitch page - Cookies - LocalStorage items",
            extra={"emoji": ":wrench:"},
        )
        cookie = {
            "domain": ".twitch.tv",
            "hostOnly": False,
            "httpOnly": False,
            "name": "auth-token",
            "path": "/",
            "SameSite": "no_restriction",
            "secure": True,
            "session": False,
            "storeId": "0",
            "id": 1,
            "value": self.auth_token,
        }
        self.browser.get(URL)
        self.browser.add_cookie(cookie)
        time.sleep(random.uniform(2.5, 3.5))

        self.__click_when_exist(
            Selectors.cookiePolicy, By.CSS_SELECTOR, suppress_error=True
        )
        time.sleep(random.uniform(0.5, 1.5))

        # Edit value in localStorage for dark theme, point consent etc.
        self.__execute_script(Javascript.localStorage)
        time.sleep(random.uniform(0.5, 1.5))
        self.__blank()

    def __blank(self):
        self.browser.get("about:blank")

    def __execute_script(self, javascript_code, suppress_error=False):
        try:
            self.browser.execute_script(javascript_code)
            return True
        except JavascriptException:
            if suppress_error is False:
                logger.warning(f"Failed to execute: {javascript_code}")
        return False

    # Private method __ - We can instantiate webdriver only with init_browser
    def __init_chrome(self):
        logger.debug("Init Chrome browser", extra={"emoji": ":wrench:"})
        options = webdriver.ChromeOptions()
        if not self.settings.show:
            options.add_argument("headless")

        options.add_argument("mute-audio")
        options.add_argument("disable-dev-shm-usage")
        options.add_argument("disable-accelerated-2d-canvas")
        options.add_argument("no-first-run")
        options.add_argument("no-zygote")
        options.add_argument("disable-gpu")
        options.add_argument("no-sandbox")
        options.add_argument("disable-setuid-sandbox")
        options.add_argument("disable-infobars")
        options.add_argument(f"user-agent={get_user_agent(self.settings.browser)}")

        options.add_experimental_option(
            "prefs", {"profile.managed_default_content_settings.images": 2}
        )
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation", "enable-logging"]
        )

        if os.path.isfile(self.settings.driver_path) is True:
            self.browser = webdriver.Chrome(self.settings.driver_path, options=options)
        else:
            logger.warning(
                f"The path {self.settings.driver_path} is not valid. Using default path...",
                extra={"emoji": ":wrench:"},
            )
            self.browser = webdriver.Chrome(options=options)

    # Private method __ - We can instantiate webdriver only with init_browser
    def __init_firefox(self):
        logger.debug("Init Firefox browser", extra={"emoji": ":wrench:"})
        options = webdriver.FirefoxOptions()
        if not self.settings.show:
            options.headless = True

        fp = webdriver.FirefoxProfile()
        fp.set_preference("permissions.default.image", 2)
        fp.set_preference("permissions.default.stylesheet", 2)
        fp.set_preference("dom.ipc.plugins.enabled.libflashplayer.so", "false")
        fp.set_preference("media.volume_scale", "0.0")
        fp.set_preference("browser.startup.homepage", "about:blank")
        fp.set_preference("startup.homepage_welcome_url", "about:blank")
        fp.set_preference("startup.homepage_welcome_url.additional", "about:blank")
        fp.set_preference(
            "general.useragent.override",
            get_user_agent(self.settings.browser),
        )

        if os.path.isfile(self.settings.driver_path) is True:
            self.browser = webdriver.Firefox(
                executable_path=self.settings.driver_path,
                options=options,
                firefox_profile=fp,
            )
        else:
            logger.warning(
                f"The path {self.settings.driver_path} is not valid. Using default path...",
                extra={"emoji": ":wrench:"},
            )
            self.browser = webdriver.Firefox(options=options, firefox_profile=fp)

    def __debug(self, event, method):
        if self.settings.do_screenshot:
            self.screenshot(f"{event.event_id}___{method}")
        if self.settings.save_html:
            self.save_html(f"{event.event_id}___{method}")

    def save_html(self, fname):
        htmls_path = os.path.join(Path().absolute(), "htmls")
        Path(htmls_path).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(htmls_path, self.session_id)).mkdir(
            parents=True, exist_ok=True
        )

        fname = f"{fname}.html" if fname.endswith(".html") is False else fname
        fname = fname.replace(".html", f".{time.time()}.html")
        fname = os.path.join(htmls_path, self.session_id, fname)

        # Little delay ...
        time.sleep(0.2)
        with open(fname, "w", encoding="utf-8") as writer:
            writer.write(self.browser.page_source)

    def screenshot(self, fname):
        screenshots_path = os.path.join(Path().absolute(), "screenshots")
        Path(screenshots_path).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(screenshots_path, self.session_id)).mkdir(
            parents=True, exist_ok=True
        )

        fname = f"{fname}.png" if fname.endswith(".png") is False else fname
        fname = fname.replace(".png", f".{time.time()}.png")
        fname = os.path.join(screenshots_path, self.session_id, fname)
        # Little pause prevent effect/css animations in browser delayed
        time.sleep(0.1)
        self.browser.save_screenshot(fname)

    def __click_when_exist(
        self, selector, by: By = By.CSS_SELECTOR, suppress_error=False, timeout=None
    ) -> bool:
        timeout = self.settings.timeout if timeout is None else timeout
        try:
            element = WebDriverWait(self.browser, timeout).until(
                expected_conditions.element_to_be_clickable((by, selector))
            )
            ActionChains(self.browser).move_to_element(element).click().perform()
            return True
        except Exception:
            if suppress_error is False:
                logger.error(f"Exception raised with: {selector}", exc_info=True)
        return False

    def __send_text(
        self, selector, text, by: By = By.CSS_SELECTOR, suppress_error=False
    ) -> bool:
        try:
            element = WebDriverWait(self.browser, self.settings.timeout).until(
                expected_conditions.element_to_be_clickable((by, selector))
            )
            ActionChains(self.browser).move_to_element(element).click().send_keys(
                text
            ).perform()
            return True
        except Exception:
            if suppress_error is False:
                logger.error(f"Exception raised with: {selector}", exc_info=True)
        return False

    def start_bet(self, event: EventPrediction):
        start_time = time.time()
        if bet_condition(self, event, logger) is True:
            for attempt in range(0, self.settings.max_attempts):
                logger.info(
                    f"Starting betting for {event} owned by {event.streamer}",
                    extra={"emoji": ":wrench:"},
                )
                self.browser.get(event.streamer.chat_url)
                time.sleep(random.uniform(3, 5))
                self.__click_when_exist(
                    Selectors.cookiePolicy,
                    By.CSS_SELECTOR,
                    suppress_error=True,
                    timeout=1.5,
                )

                # Hide the chat ... Don't ask me why
                self.__execute_script(Javascript.clearStyleChat, suppress_error=True)

                if self.__bet_chains_methods(event) is True:
                    return self.currently_is_betting, time.time() - start_time
                logger.error(
                    f"Attempt {attempt+1} failed!", extra={"emoji": ":wrench:"}
                )
            self.__blank()  # If we fail return to blank page
        return False, time.time() - start_time

    def __bet_chains_methods(self, event) -> bool:
        if self.__open_coins_menu(event) is True:
            if self.__click_on_bet(event) is True:
                if self.__enable_custom_bet_value(event) is True:
                    return True
        return False

    def place_bet(self, event: EventPrediction):
        logger.info(
            f"Going to complete bet for {event} owned by {event.streamer}",
            extra={"emoji": ":wrench:"},
        )
        if event.status == "ACTIVE":
            if event.box_fillable and self.currently_is_betting:

                div_bet_is_open = False
                self.__debug(event, "place_bet")
                try:
                    WebDriverWait(self.browser, 1).until(
                        expected_conditions.visibility_of_element_located(
                            (By.XPATH, Selectors.betMainDivXP)
                        )
                    )
                    div_bet_is_open = True
                except TimeoutException:
                    logger.info(
                        "The bet div was not found, maybe It was closed. Attempting to open again... Hopefully in time!",
                        extra={"emoji": ":wrench:"},
                    )
                    div_bet_is_open = self.__bet_chains_methods(event)
                    if div_bet_is_open is True:
                        logger.info(
                            "Success! Bet div is now open, we can complete the bet!",
                            extra={"emoji": ":wrench:"},
                        )

                if div_bet_is_open is True:
                    decision = event.bet.calculate(event.streamer.channel_points)
                    if decision["choice"] is not None:
                        selector_index = 1 if decision["choice"] == "A" else 2
                        logger.info(
                            f"Decision: {event.bet.get_outcome(selector_index - 1)}",
                            extra={"emoji": ":wrench:"},
                        )

                        try:
                            logger.info(
                                f"Going to write: {millify(decision['amount'])} channel points on input {decision['choice']}",
                                extra={"emoji": ":wrench:"},
                            )
                            if (
                                self.__send_text_on_bet(
                                    event, selector_index, decision["amount"]
                                )
                                is True
                            ):
                                logger.info(
                                    f"Going to place the bet for {event}",
                                    extra={"emoji": ":wrench:"},
                                )
                                if self.__click_on_vote(event, selector_index) is True:
                                    event.bet_placed = True
                                    time.sleep(random.uniform(5, 10))
                        except Exception:
                            logger.error("Exception raised", exc_info=True)
                else:
                    logger.info(
                        "Sorry, unable to complete the bet. The bet div is still closed!"
                    )
            else:
                logger.info(
                    f"Sorry, unable to complete the bet. Event box fillable: {event.box_fillable}, the browser is betting: {self.currently_is_betting}"
                )
        else:
            logger.info(
                f"Oh no! The event is not active anymore! Current status: {event.status}",
                extra={"emoji": ":disappointed_relieved:"},
            )

        self.browser.get("about:blank")
        self.currently_is_betting = False

    def __open_coins_menu(self, event: EventPrediction) -> bool:
        logger.info(f"Opening coins menu for {event}", extra={"emoji": ":wrench:"})
        status = self.__click_when_exist(Selectors.coinsMenuXP, By.XPATH)
        if status is False:
            status = self.__execute_script(Javascript.coinsMenu)

        if status is True:
            time.sleep(random.uniform(0.01, 0.1))
            self.__debug(event, "open_coins_menu")
            return True
        return False

    def __click_on_bet(self, event, maximize_div=True) -> bool:
        logger.info(f"Clicking on the bet for {event}", extra={"emoji": ":wrench:"})
        if self.__click_when_exist(Selectors.betTitle, By.CSS_SELECTOR) is True:
            time.sleep(random.uniform(0.01, 0.1))
            if maximize_div is True:
                # Edit the css for make the window full-screen in browser. Another useless change
                self.__execute_script(Javascript.maximizeBetWindow, suppress_error=True)
            self.__debug(event, "click_on_bet")
            return True
        return False

    def __enable_custom_bet_value(self, event, scroll_down=True) -> bool:
        logger.info(
            f"Enable input of custom value for {event}",
            extra={"emoji": ":wrench:"},
        )

        if scroll_down is True:
            time.sleep(random.uniform(0.01, 0.1))
            if self.__execute_script(Javascript.scrollDownBetWindow) is False:
                logger.error("Unable to scroll down in the bet window!")

        status = self.__click_when_exist(Selectors.betCustomVote, By.CSS_SELECTOR)
        if status is False:
            status = self.__execute_script(Javascript.betCustomVote)

        if status is True:
            time.sleep(random.uniform(0.01, 0.1))
            self.__debug(event, "enable_custom_bet_value")
            event.box_fillable = True
            self.currently_is_betting = True
            return True
        else:
            logger.info(
                "Something went wrong unable to continue with betting - Fillable box not available!"
            )
        return False

    def __send_text_on_bet(self, event, selector_index, text) -> bool:
        self.__debug(event, "before__send_text")
        status = self.__send_text(
            f"{Selectors.betVoteInputXP}[{selector_index}]", text, By.XPATH
        )
        if status is False:
            status = self.__execute_script(
                Javascript.betVoteInput.format(int(selector_index) - 1, int(text))
            )

        if status is True:
            self.__debug(event, "send_text")
            return True
        return False

    def __click_on_vote(self, event, selector_index) -> bool:
        status = self.__click_when_exist(
            f"{Selectors.betVoteButtonXP}[{selector_index}]", By.XPATH
        )
        if status is False:
            status = self.__execute_script(
                Javascript.betVoteButton.format(int(selector_index) - 1)
            )

        if status is True:
            self.__debug(event, "click_on_vote")
            return True
        return False
