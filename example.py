from TwitchChannelPointsMiner import TwitchChannelPointsMiner
from TwitchChannelPointsMiner.classes.Bet import Strategy, BetSettings
from TwitchChannelPointsMiner.classes.TwitchBrowser import Browser, BrowserSettings

twitch_miner = TwitchChannelPointsMiner(
    username="your-twitch-username",
    make_predictions=True,  # If you want to Bet / Make prediction
    follow_raid=True,  # Follow raid to obtain more points
    save_logs=True,  # Save logs in file
    browser_settings=BrowserSettings(
        browser=Browser.FIREFOX,  # Choose if you want to use Chrome or Firefox as browser
        show=False,  # Show the browser during bet
        do_screenshot=False,  # Do screenshot during the bet
    ),
    bet_strategy=BetSettings(
        strategy=Strategy.SMART,  # Choose you strategy!
        percentage=5,  # Place the x% of your channel points
        percentage_gap=20,  # Gap difference between outcomesA and outcomesB (for SMART stragegy)
        max_points=50000,  # If the x percetage of your channel points is gt bet_max_points set this value
    )
)

twitch_miner.mine(["streamer1", "streamer2"])  # Array of streamers
