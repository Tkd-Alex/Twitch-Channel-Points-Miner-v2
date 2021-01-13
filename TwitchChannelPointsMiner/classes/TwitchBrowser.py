import time
import logging
import random

from datetime import datetime
from enum import Enum, auto
from PIL import Image, ImageDraw, ImageFont

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from TwitchChannelPointsMiner.classes.EventPrediction import EventPrediction

TWITCH_URL = "https://www.twitch.tv/"

cookiePolicyQuery = 'button[data-a-target="consent-banner-accept"]'
streamCoinsMenu = '//div[@data-test-selector="community-points-summary"]//button'
streamBetTitleInBet = '[data-test-selector="predictions-list-item__title"]'
streamBetCustomVote = (
    '[data-test-selector="prediction-checkout-active-footer__input-type-toggle"]'
)
streamBetVoteInput = (
    "(//input[contains(@class,'tw-block tw-border-bottom-left-radius-medium')])"
)
streamBetVoteButton = "(//div[@id='channel-points-reward-center-body']//button)"

logger = logging.getLogger(__name__)


class Browser(Enum):
    CHROME = auto()
    FIREFOX = auto()


class TwitchBrowser:
    def __init__(self, auth_token: str, timeout: float = 5.0):
        self.auth_token = auth_token
        self.timeout = timeout
        self.currently_is_betting = False
        self.browser = None

    def init(self, show: bool = True, browser: Browser = Browser.FIREFOX):
        if browser == Browser.FIREFOX:
            self.__init_firefox(show)
        elif browser == Browser.CHROME:
            self.__init_chrome(show)

        if self.browser is not None:
            self.browser.set_window_size(250, 900)
            self.browser.implicitly_wait(2)

        self.__init_twitch()

    def __init_twitch(self):
        logger.info("⚙️  Init Twitch page - Cookie - LocalStorage items")
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
        self.browser.get(TWITCH_URL)
        self.browser.add_cookie(cookie)

        self.__click_when_exist(cookiePolicyQuery, By.CSS_SELECTOR)
        time.sleep(1.5)

        # Edit value in localStorage for dark theme, point consent etc.
        self.browser.execute_script(
            """
            window.localStorage.setItem("volume", 0);
            window.localStorage.setItem("channelPointsOnboardingDismissed", true);
            window.localStorage.setItem("twilight.theme", 1);
            window.localStorage.setItem("mature", true);
            window.localStorage.setItem("rebrand-notice-dismissed", true);
        """
        )
        time.sleep(1.5)
        self.__blank()

    def __blank(self):
        self.browser.get("about:blank")

    # Private method __ - We can instantiate webdriver only with init_browser
    def __init_chrome(self, show):
        logger.info("⚙️  Init Chrome browser")
        options = webdriver.ChromeOptions()
        options.add_argument("--mute-audio")
        if not show:
            options.add_argument("headless")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-accelerated-2d-canvas")
        options.add_argument("--no-first-run")
        options.add_argument("--no-zygote")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.browser = webdriver.Chrome(options=options)

    # Private method __ - We can instantiate webdriver only with init_browser
    def __init_firefox(self, show):
        logger.info("⚙️  Init Firefox browser")
        options = webdriver.FirefoxOptions()
        if not show:
            options.headless = True

        fp = webdriver.FirefoxProfile()
        fp.set_preference("permissions.default.image", 2)
        fp.set_preference("permissions.default.stylesheet", 2)
        fp.set_preference("dom.ipc.plugins.enabled.libflashplayer.so", "false")
        fp.set_preference("media.volume_scale", "0.0")
        fp.set_preference("browser.startup.homepage", "about:blank")
        fp.set_preference("startup.homepage_welcome_url", "about:blank")
        fp.set_preference("startup.homepage_welcome_url.additional", "about:blank")

        self.browser = webdriver.Firefox(options=options, firefox_profile=fp)

    def screenshot(self, fname, write_timestamp=True):
        self.browser.save_screenshot(fname)

        if write_timestamp is True:
            image = Image.open(fname)
            draw = ImageDraw.Draw(image)

            font = ImageFont.truetype("./Roboto/Roboto-Bold.ttf", size=35)
            (x, y) = (15, image.height // 3)
            datetime_text = datetime.now().strftime("%d/%m %H:%M:%S.%f")

            shadowcolor = "rgb(0, 0, 0)"  # black color
            # Thin border
            draw.text((x - 1, y), datetime_text, font=font, fill=shadowcolor)
            draw.text((x + 1, y), datetime_text, font=font, fill=shadowcolor)
            draw.text((x, y - 1), datetime_text, font=font, fill=shadowcolor)
            draw.text((x, y + 1), datetime_text, font=font, fill=shadowcolor)

            # Thicker border
            draw.text((x - 1, y - 1), datetime_text, font=font, fill=shadowcolor)
            draw.text((x + 1, y - 1), datetime_text, font=font, fill=shadowcolor)
            draw.text((x - 1, y + 1), datetime_text, font=font, fill=shadowcolor)
            draw.text((x + 1, y + 1), datetime_text, font=font, fill=shadowcolor)

            color = "rgb(255, 255, 255)"  # white color
            draw.text((x, y), datetime_text, font=font, fill=color)
            image.save(fname, optimize=True, quality=20)

    def __click_when_exist(self, selector, by: By = By.CSS_SELECTOR):
        try:
            element = WebDriverWait(self.browser, self.timeout).until(
                expected_conditions.element_to_be_clickable((by, selector))
            )
            ActionChains(self.browser).move_to_element(element).click().perform()
            return element
        except Exception:
            logger.error(f"Exception raised with: {selector}", exc_info=True)
        finally:
            return None

    def __send_text(self, selector, text, by: By = By.CSS_SELECTOR):
        try:
            element = WebDriverWait(self.browser, self.timeout).until(
                expected_conditions.element_to_be_clickable((By.XPATH, selector))
            )
            ActionChains(self.browser, self.timeout).move_to_element(
                element
            ).click().send_keys(text).perform()
            return element
        except Exception:
            logger.error(f"Exception raised with: {selector}", exc_info=True)
        finally:
            return None

    def start_bet(self, event: EventPrediction):
        if self.currently_is_betting:
            logger.info(
                "Sorry, unable to start the bet. The browser it's currently betting another event"
            )
        else:
            logger.info(
                f"⚙️  Start betting at {event.streamer.chat_url} for event: {event}"
            )
            self.browser.get(event.streamer.chat_url)
            time.sleep(random.uniform(4, 6))
            self.__open_coins_menu(event)
            self.__click_on_bet(event)
            self.__enable_custom_bet_value(event)
            return self.currently_is_betting

    def complete_bet(self, event: EventPrediction):
        logger.info(
            f"⚙️  Going to complete bet for event {event}. Current url page: {self.browser.current_url}"
        )
        if event.box_fillable and self.currently_is_betting:
            decision = event.bet.calculate(event.streamer.channel_points)
            if decision["choice"]:
                selector_index = "[1]" if decision["choice"] == "A" else "[2]"

                try:
                    logger.info(
                        f"⚙️  Going to write: {decision['amount']} on input {decision['choice']}"
                    )
                    self.__send_text(
                        streamBetVoteInput + selector_index,
                        decision["amount"],
                        By.XPATH,
                    )
                    if self.do_screenshot:
                        self.screenshot(
                            "./tmp/{}_TEXT_WRITE.png".format(event.event_id)
                        )

                    logger.info("Going to place the bet")
                    self.__click_when_exist(
                        streamBetVoteButton + selector_index, By.XPATH
                    )
                    if self.do_screenshot:
                        self.screenshot(
                            "./tmp/{}_CLICK_ON_VOTE.png".format(event.event_id)
                        )

                    time.sleep(random.uniform(15, 25))
                    event.bet_completed = True

                    self.browser.get("about:blank")
                    self.currently_is_betting = False

                except Exception:
                    logger.error("Exception raised", exc_info=True)

                    self.browser.get("about:blank")
                    self.currently_is_betting = False

        else:
            logger.info(
                f"Sorry, unable to complete the bet. Event box fillable: {event.box_fillable}, the browser is betting: {self.currently_is_betting}"
            )

    def __open_coins_menu(self, event: EventPrediction):
        logger.info(f"⚙️  Open coins menu for event: {event}")
        self.__click_when_exist(streamCoinsMenu, By.XPATH)
        time.sleep(random.uniform(0.05, 0.1))
        if self.do_screenshot:
            self.screenshot("./tmp/{}_OPEN_COINS.png".format(event.event_id))

    def __click_on_bet(self, event):
        logger.info(f"⚙️  Click on the bet for event: {event}")
        self.__click_when_exist(streamBetTitleInBet, By.CSS_SELECTOR)
        time.sleep(random.uniform(0.05, 0.1))
        if self.do_screenshot:
            self.screenshot("./tmp/{}_CLICK_ON_BET.png".format(event.event_id))

    def __enable_custom_bet_value(self, event):
        logger.info(f"⚙️  Enable input of custom value for event: {event}")
        if self.__click_when_exist(streamBetCustomVote, By.CSS_SELECTOR) is not None:
            time.sleep(random.uniform(0.05, 0.1))
            if self.do_screenshot:
                self.screenshot("./tmp/{}_INPUT_ENABLE.png".format(event.event_id))

            event.box_fillable = True
            self.currently_is_betting = True
        else:
            logger.info(
                "Something whent wrong unable to continue with betting - Fillable box not avaible"
            )
