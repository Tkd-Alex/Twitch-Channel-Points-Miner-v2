from TwitchChannelPointsMiner import TwitchChannelPointsMiner

twitch_miner = TwitchChannelPointsMiner(
    username="your-twitch-username",
    make_predictions=True,  # If you want to Bet / Make prediction
    follow_raid=True,  # Follow raid to obtain more points
    save_logs=True,  # Save logs in file
)

twitch_miner.mine(["streamer1", "streamer2"])  # Array of streamers
