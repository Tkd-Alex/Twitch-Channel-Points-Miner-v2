from TwitchChannelPointsMiner import TwitchChannelPointsMiner
from TwitchChannelPointsMiner.classes.Bet import Strategy

twitch_miner = TwitchChannelPointsMiner(
    username="your-twitch-username",
    make_predictions=True,  # If you want to Bet / Make prediction
    follow_raid=True,  # Follow raid to obtain more points
    save_logs=True,  # Save logs in file
    show_browser=False,  # Show the browser during bet
    do_browser_screenshot=False,  # Do screenshot during the bet
    bet_strategy=Strategy.SMART,  # Choose you strategy!
    bet_percentage=5,  # Place the x% of your channel points
    bet_percentage_gap=20,  # Gap difference between outcomesA and outcomesB (for SMART stragegy)
    bet_max_points=50000,  # If the x percetage of your channel points is gt bet_max_points set this value
)

twitch_miner.mine(["streamer1", "streamer2"])  # Array of streamers
