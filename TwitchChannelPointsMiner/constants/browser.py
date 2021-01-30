USER_AGENTS = {
    "Windows": {
        "CHROME": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
        "FIREFOX": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
    },
    "Linux": {
        "CHROME": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
        "FIREFOX": "Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0",
    },
}


class Selectors:
    # XPath Selector and Javascript helpers
    cookiePolicy = 'button[data-a-target="consent-banner-accept"]'
    coinsMenuXP = '//div[@data-test-selector="community-points-summary"]//button'
    betTitle = '[data-test-selector="predictions-list-item__title"]'
    betCustomVote = "button[data-test-selector='prediction-checkout-active-footer__input-type-toggle']"
    betMainDivXP = "//div[@id='channel-points-reward-center-body']//div[contains(@class,'custom-prediction-button')]"
    betVoteInputXP = f"({betMainDivXP}//input)"
    betVoteButtonXP = f"({betMainDivXP}//button)"


class Javascript:
    # Helpers for selenium. I think is very useless
    coinsMenu = 'document.querySelector("[data-test-selector=\'community-points-summary\']").getElementsByTagName("button")[0].click();'
    betVoteInput = 'document.getElementById("channel-points-reward-center-body").getElementsByTagName("input")[{}].value = {};'
    betVoteButton = 'document.getElementById("channel-points-reward-center-body").getElementsByTagName("button")[{}].click();'
    betCustomVote = f'document.querySelector("{Selectors.betCustomVote}").click();'

    # Some Javascript code that should help the script
    localStorage = """
    window.localStorage.setItem("volume", 0);
    window.localStorage.setItem("channelPointsOnboardingDismissed", true);
    window.localStorage.setItem("twilight.theme", 1);
    window.localStorage.setItem("mature", true);
    window.localStorage.setItem("rebrand-notice-dismissed", true);
    window.localStorage.setItem("emoteAnimationsEnabled", false);
    window.localStorage.setItem("chatPauseSetting", "ALTKEY");
    """
    clearStyleChat = """
    var item = document.querySelector('[data-test-selector="chat-scrollable-area__message-container"]');
    if (item) {
        var parent = item.closest("div.simplebar-scroll-content");
        if(parent) parent.hidden = true;
    }
    var header = document.querySelector('[data-test-selector="channel-leaderboard-container"]');
    if(header) header.hidden = true;
    """
    maximizeBetWindow = """
    var absolute = document.querySelector('[aria-describedby="channel-points-reward-center-body"]').closest("div.tw-absolute")
    if(absolute) absolute.classList.remove("tw-absolute")

    document.getElementsByClassName("reward-center__content")[0].style.width = "44rem";
    document.getElementsByClassName("reward-center__content")[0].style.height = "55rem";

    document.querySelector('[aria-describedby="channel-points-reward-center-body"]').style["max-height"] = "55rem";

    document.getElementsByClassName("reward-center-body")[0].style["max-width"] = "44rem";
    // document.getElementsByClassName("reward-center-body")[0].style["min-height"] = "55rem";
    """
    scrollDownBetWindow = """
    var scrollable = document.getElementById("channel-points-reward-center-body").closest("div.simplebar-scroll-content");
    scrollable.scrollTop = scrollable.scrollHeight;
    """
