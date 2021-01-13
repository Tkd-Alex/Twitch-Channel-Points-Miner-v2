# Twitch Channel Points Miner - v2

This is a fork of: https://github.com/gottagofaster236/Twitch-Channel-Points-Miner. <br>
I've also take some piece of code - and idea to use Selenium fo do bet from: https://github.com/ClementRoyer/TwitchAutoCollect-AutoBet

> A simple script that will watch a stream for you and earn the channel points.

> It can wait for a streamer to go live (+_450 points_ when the stream starts), it will automatically click the bonus button (_+50 points_), and it will follow raids (_+250 points_).

Read more here: https://help.twitch.tv/s/article/channel-points-guide?language=en_US

![Screenshot](./screenshot.png)

## Main difference from the original repository:

- Improve the logging
- Rewrite the entire code using classe instead of module with global variables
- Place the bet / make - prediction and won or lose (good luck) your channel points!

## How to use:
1. Clone or download this repository `git clone https://github.com/Tkd-Alex/Twitch-Channel-Points-Miner`
2. Install all the requirements `pip install -r requirements.txt`
3. Create your `run.py` file start from [example.py](/example.py)
```python
from TwitchChannelPointsMiner import TwitchChannelPointsMiner

twitch_miner = TwitchChannelPointsMiner(
    username="your-twitch-username",
    make_predictions=True,  # If you want to Bet / Make prediction
    follow_raid=True,  # Follow raid to obtain more points
    save_logs=True,  # Save logs in file
)

twitch_miner.mine(["streamer1", "streamer2"])  # Array of streamers
```
4. Start mining! `python run.py`

## Migrating from old repository:
If you already have a `twitch-cookies.pkl` and you don't want to login again please create a `cookies/` folder in the current directory and then copy the .pkl file with a new name `your-twitch-username.pkl`
```
.
+-- run.py
+-- cookies
|   +-- your-twitch-username.pkl
```