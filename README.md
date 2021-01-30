# Twitch Channel Points Miner - v2

**Credits**
- Main idea: https://github.com/gottagofaster236/Twitch-Channel-Points-Miner
- Bet system (Selenium): https://github.com/ClementRoyer/TwitchAutoCollect-AutoBet

> A simple script that will watch a stream for you and earn the channel points.

> It can wait for a streamer to go live (+_450 points_ when the stream starts), it will automatically click the bonus button (_+50 points_), and it will follow raids (_+250 points_).

Read more about channels point [here](https://help.twitch.tv/s/article/channel-points-guide)

## Main difference from the original repository:

- Improve the logging
- Final report with all the datas
- Rewrite the entire code using classe instead of module with global variables
- Automatic download the followers list and use as input
- Better 'Watch Streak' strategy in priority system [#11](https://github.com/Tkd-Alex/Twitch-Channel-Points-Miner-v2/issues/11)
- Auto claim game drops from Twitch inventory [#21](https://github.com/Tkd-Alex/Twitch-Channel-Points-Miner-v2/issues/21) Read more about game drops [here](https://help.twitch.tv/s/article/mission-based-drops)
- Place the bet / make prediction and won or lose (good luck) your channel points! **(CURRENTLY IN BETA)**

For the bet system the script use Selenium. Could be usefull understand how to MakePrediction usign a [POST] request. I've also write a [poc](/TwitchChannelPointsMiner/classes/Twitch.py#L160) but I don't know how to calculate/create the transactionID. Any helps are welcome

### Full logs
```
%d/%m/%y %H:%M:%S - INFO - [run]: 💣  Start session: '9eb934b0-1684-4a62-b3e2-ba097bd67d35'
%d/%m/%y %H:%M:%S - INFO - [run]: 🤓  Loading data for x streamers. Please wait ...
%d/%m/%y %H:%M:%S - INFO - [set_offline]: 😴  Streamer(username=streamer-username1, channel_id=0000000, channel_points=67247) is Offline!
%d/%m/%y %H:%M:%S - INFO - [set_offline]: 😴  Streamer(username=streamer-username2, channel_id=0000000, channel_points=4240) is Offline!
%d/%m/%y %H:%M:%S - INFO - [set_offline]: 😴  Streamer(username=streamer-username3, channel_id=0000000, channel_points=61365) is Offline!
%d/%m/%y %H:%M:%S - INFO - [set_offline]: 😴  Streamer(username=streamer-username4, channel_id=0000000, channel_points=3760) is Offline!
%d/%m/%y %H:%M:%S - INFO - [set_online]: 🥳  Streamer(username=streamer-username, channel_id=0000000, channel_points=61365) is Online!
%d/%m/%y %H:%M:%S - INFO - [start_bet]: 🔧  Start betting for EventPrediction(event_id=xxxx-xxxx-xxxx-xxxx, title=Please star this repo) owned by Streamer(username=streamer-username, channel_id=0000000, channel_points=61365)
%d/%m/%y %H:%M:%S - INFO - [__open_coins_menu]: 🔧  Open coins menu for EventPrediction(event_id=xxxx-xxxx-xxxx-xxxx, title=Please star this repo)
%d/%m/%y %H:%M:%S - INFO - [__click_on_bet]: 🔧  Click on the bet for EventPrediction(event_id=xxxx-xxxx-xxxx-xxxx, title=Please star this repo)
%d/%m/%y %H:%M:%S - INFO - [__enable_custom_bet_value]: 🔧  Enable input of custom value for EventPrediction(event_id=xxxx-xxxx-xxxx-xxxx, title=Please star this repo)
%d/%m/%y %H:%M:%S - INFO - [on_message]: ⏰  Place the bet after: 89.99s for: EventPrediction(event_id=xxxx-xxxx-xxxx-xxxx-15c61914ef69, title=Please star this repo)
%d/%m/%y %H:%M:%S - INFO - [on_message]: 🚀  +12 → Streamer(username=streamer-username, channel_id=0000000, channel_points=61377) - Reason: WATCH.
%d/%m/%y %H:%M:%S - INFO - [place_bet]: 🔧  Going to complete bet for EventPrediction(event_id=xxxx-xxxx-xxxx-xxxx, title=Please star this repo) owned by Streamer(username=streamer-username, channel_id=0000000, channel_points=61365)
%d/%m/%y %H:%M:%S - INFO - [place_bet]: 🔧  Decision: YES (PINK), Points: 156k, Users: 46 (61.33%), Odds: 1.57 (63.69%)
%d/%m/%y %H:%M:%S - INFO - [place_bet]: 🔧  Going to write: 4296 channel points on input B
%d/%m/%y %H:%M:%S - INFO - [place_bet]: 🔧  Going to place the bet for EventPrediction(event_id=xxxx-xxxx-xxxx-xxxx, title=Please star this repo)
%d/%m/%y %H:%M:%S - INFO - [on_message]: 🚀  +6675 → Streamer(username=streamer-username, channel_id=0000000, channel_points=64206) - Reason: PREDICTION.
%d/%m/%y %H:%M:%S - INFO - [on_message]: 📊  EventPrediction(event_id=xxxx-xxxx-xxxx-xxxx, title=Please star this repo) - Result: WIN, Points won: 6675
%d/%m/%y %H:%M:%S - INFO - [on_message]: 🚀  +12 → Streamer(username=streamer-username, channel_id=0000000, channel_points=64218) - Reason: WATCH.
%d/%m/%y %H:%M:%S - INFO - [on_message]: 🚀  +12 → Streamer(username=streamer-username, channel_id=0000000, channel_points=64230) - Reason: WATCH.
%d/%m/%y %H:%M:%S - INFO - [claim_bonus]: 🎁  Claiming the bonus for Streamer(username=streamer-username, channel_id=0000000, channel_points=64230)!
%d/%m/%y %H:%M:%S - INFO - [on_message]: 🚀  +60 → Streamer(username=streamer-username, channel_id=0000000, channel_points=64290) - Reason: CLAIM.
%d/%m/%y %H:%M:%S - INFO - [on_message]: 🚀  +12 → Streamer(username=streamer-username, channel_id=0000000, channel_points=64326) - Reason: WATCH.
%d/%m/%y %H:%M:%S - INFO - [on_message]: 🚀  +400 → Streamer(username=streamer-username, channel_id=0000000, channel_points=64326) - Reason: WATCH_STREAK.
%d/%m/%y %H:%M:%S - INFO - [claim_bonus]: 🎁  Claiming the bonus for Streamer(username=streamer-username, channel_id=0000000, channel_points=64326)!
%d/%m/%y %H:%M:%S - INFO - [on_message]: 🚀  +60 → Streamer(username=streamer-username, channel_id=0000000, channel_points=64386) - Reason: CLAIM.
%d/%m/%y %H:%M:%S - INFO - [on_message]: 🚀  +12 → Streamer(username=streamer-username, channel_id=0000000, channel_points=64398) - Reason: WATCH.
%d/%m/%y %H:%M:%S - INFO - [update_raid]: 🎭  Joining raid from Streamer(username=streamer-username, channel_id=0000000, channel_points=64398) to another-username!
%d/%m/%y %H:%M:%S - INFO - [on_message]: 🚀  +250 → Streamer(username=streamer-username, channel_id=0000000, channel_points=6845) - Reason: RAID.
```
### Less logs
```
%d/%m %H:%M:%S - 💣  Start session: '9eb934b0-1684-4a62-b3e2-ba097bd67d35'
%d/%m %H:%M:%S - 🤓  Loading data for 13 streamers. Please wait ...
%d/%m %H:%M:%S - 😴  streamer-username1 (xxx points) is Offline!
%d/%m %H:%M:%S - 😴  streamer-username2 (xxx points) is Offline!
%d/%m %H:%M:%S - 😴  streamer-username3 (xxx points) is Offline!
%d/%m %H:%M:%S - 😴  streamer-username4 (xxx points) is Offline!
%d/%m %H:%M:%S - 🥳  streamer-username (xxx points) is Online!
%d/%m %H:%M:%S - 🔧  Start betting for EventPrediction: Please star this repo owned by streamer-username (xxx points)
%d/%m %H:%M:%S - 🔧  Open coins menu for EventPrediction: Please star this repo
%d/%m %H:%M:%S - 🔧  Click on the bet for EventPrediction: Please star this repo
%d/%m %H:%M:%S - 🔧  Enable input of custom value for EventPrediction: Please star this repo
%d/%m %H:%M:%S - ⏰  Place the bet after: 89.99s EventPrediction: Please star this repo
%d/%m %H:%M:%S - 🚀  +12 → streamer-username (xxx points) - Reason: WATCH.
%d/%m %H:%M:%S - 🔧  Going to complete bet for EventPrediction: Please star this repo owned by streamer-username (xxx points)
%d/%m %H:%M:%S - 🔧  Decision: YES (PINK), Points: 156k, Users: 46 (61.33%), Odds: 1.57 (63.69%)
%d/%m %H:%M:%S - 🔧  Going to write: 4296 channel points on input B
%d/%m %H:%M:%S - 🔧  Going to place the bet for EventPrediction: Please star this repo
%d/%m %H:%M:%S - 🚀  +6675 → streamer-username (xxx points) - Reason: PREDICTION.
%d/%m %H:%M:%S - 📊  EventPrediction: Please star this repo - Result: WIN, Points won: 6675
%d/%m %H:%M:%S - 🚀  +12 → streamer-username (xxx points) - Reason: WATCH.
%d/%m %H:%M:%S - 🚀  +12 → streamer-username (xxx points) - Reason: WATCH.
%d/%m %H:%M:%S - 🚀  +60 → streamer-username (xxx points) - Reason: CLAIM.
%d/%m %H:%M:%S - 🚀  +12 → streamer-username (xxx points) - Reason: WATCH.
%d/%m %H:%M:%S - 🚀  +400 → streamer-username (xxx points) - Reason: WATCH_STREAK.
%d/%m %H:%M:%S - 🚀  +60 → streamer-username (xxx points) - Reason: CLAIM.
%d/%m %H:%M:%S - 🚀  +12 → streamer-username (xxx points) - Reason: WATCH.
%d/%m %H:%M:%S - 🎭  Joining raid from streamer-username (xxx points) to another-username!
%d/%m %H:%M:%S - 🚀  +250 → streamer-username (xxx points) - Reason: RAID.
```
### Final report:
```
%d/%m/%y %H:%M:%S - 🛑  End session 'f738d438-cdbc-4cd5-90c4-1517576f1299'
%d/%m/%y %H:%M:%S - 📄  Logs file: /.../path/Twitch-Channel-Points-Miner-v2/logs/username.timestamp.log
%d/%m/%y %H:%M:%S - ⌛  Duration 10:29:19.547371

%d/%m/%y %H:%M:%S - 📊  BetSettings(Strategy=Strategy.SMART, Percentage=7, PercentageGap=20, MaxPoints=7500
%d/%m/%y %H:%M:%S - 📊  EventPrediction(event_id=xxxx-xxxx-xxxx-xxxx, title="Event Title1")
		Streamer(username=streamer-username, channel_id=0000000, channel_points=67247)
		Bet(TotalUsers=1k, TotalPoints=11M), Decision={'choice': 'B', 'amount': 5289, 'id': 'xxxx-yyyy-zzzz'})
		Outcome0(YES (BLUE) Points: 7M, Users: 641 (58.49%), Odds: 1.6, (5}%)
		Outcome1(NO (PINK),Points: 4M, Users: 455 (41.51%), Odds: 2.65 (37.74%))
		Result: {'type': 'LOSE', 'won': 0}
%d/%m/%y %H:%M:%S - 📊  EventPrediction(event_id=yyyy-yyyy-yyyy-yyyy, title="Event Title2")
		Streamer(username=streamer-username, channel_id=0000000, channel_points=3453464)
		Bet(TotalUsers=921, TotalPoints=11M), Decision={'choice': 'A', 'amount': 4926, 'id': 'xxxx-yyyy-zzzz'})
		Outcome0(YES (BLUE) Points: 9M, Users: 562 (61.02%), Odds: 1.31 (76.34%))
		Outcome1(YES (PINK) Points: 3M, Users: 359 (38.98%), Odds: 4.21 (23.75%))
		Result: {'type': 'WIN', 'won': 6531}
%d/%m/%y %H:%M:%S - 📊  EventPrediction(event_id=ad152117-251b-4666-b683-18e5390e56c3, title="Event Title3")
		Streamer(username=streamer-username, channel_id=0000000, channel_points=45645645)
		Bet(TotalUsers=260, TotalPoints=3M), Decision={'choice': 'A', 'amount': 5054, 'id': 'xxxx-yyyy-zzzz'})
		Outcome0(YES (BLUE) Points: 689k, Users: 114 (43.85%), Odds: 4.24 (23.58%))
		Outcome1(NO (PINK) Points: 2M, Users: 146 (56.15%), Odds: 1.31 (76.34%))
		Result: {'type': 'LOSE', 'won': 0}

%d/%m/%y %H:%M:%S - 🎤  Streamer(username=streamer-username, channel_id=0000000, channel_points=67247), Gained (end-start): -7838
%d/%m/%y %H:%M:%S - 💰  WATCH(35 times, 350 gained), CLAIM(11 times, 550 gained), PREDICTION(1 times, 6531 gained)
%d/%m/%y %H:%M:%S - 🎤  Streamer(username=streamer-username1, channel_id=0000000, channel_points=4240), Gained (end-start): 0
%d/%m/%y %H:%M:%S - 🎤  Streamer(username=streamer-username2, channel_id=0000000, channel_points=61365), Gained (end-start): 977
%d/%m/%y %H:%M:%S - 💰  WATCH(11 times, 132 gained), REFUND(1 times, 605 gained), CLAIM(4 times, 240 gained)
%d/%m/%y %H:%M:%S - 🎤  Streamer(username=streamer-username3, channel_id=0000000, channel_points=6815), Gained (end-start): 0
%d/%m/%y %H:%M:%S - 🎤  Streamer(username=streamer-username4, channel_id=0000000, channel_points=16386), Gained (end-start): 0
%d/%m/%y %H:%M:%S - 🎤  Streamer(username=streamer-username5, channel_id=0000000, channel_points=25960), Gained (end-start): 1680
%d/%m/%y %H:%M:%S - 💰  WATCH(53 times, 530 gained), CLAIM(17 times, 850 gained)
%d/%m/%y %H:%M:%S - 🎤  Streamer(username=streamer-username6, channel_id=0000000, channel_points=9430), Gained (end-start): 1120
%d/%m/%y %H:%M:%S - 💰  WATCH(42 times, 420 gained), WATCH_STREAK(1 times, 450 gained), CLAIM(14 times, 700 gained)
%d/%m/%y %H:%M:%S - 🎤  Streamer(username=streamer-username7, channel_id=0000000, channel_points=2380), Gained (end-start): 0
%d/%m/%y %H:%M:%S - 🎤  Streamer(username=streamer-username8, channel_id=0000000, channel_points=10230), Gained (end-start): 0
```

## How to use:
1. Clone this repository `git clone https://github.com/Tkd-Alex/Twitch-Channel-Points-Miner-v2`
2. Install all the requirements `pip install -r requirements.txt`
3. Create your `run.py` file start from [example.py](/example.py)
```python
# -*- coding: utf-8 -*-

import logging
from TwitchChannelPointsMiner import TwitchChannelPointsMiner
from TwitchChannelPointsMiner.logger import LoggerSettings
from TwitchChannelPointsMiner.classes.entities.Bet import Strategy, BetSettings
from TwitchChannelPointsMiner.classes.TwitchBrowser import Browser, BrowserSettings

twitch_miner = TwitchChannelPointsMiner(
    username="your-twitch-username",
    make_predictions=True,              # If you want to Bet / Make prediction | The browser will never start
    follow_raid=True,                   # Follow raid to obtain more points
    watch_streak=True,                  # If a streamer go online change the priotiry of streamers array and catch the watch screak. Issue #11
    drops_events=True,                  # If you want to auto claim game drops from Twitch inventory Issue #21
    claim_drops_startup=False,          # If you want to auto claim all drops from Twitch inventory on startup
    logger_settings=LoggerSettings(
        save=True,                      # If you want to save logs in file (suggested)
        console_level=logging.INFO,     # Level of logs - use logging.DEBUG for more info)
        file_level=logging.DEBUG,       # Level of logs - If you think the log file it's too big use logging.INFO
        emoji=True,                     # On Windows we have a problem to print emoji. Set to false if you have a problem
        less=False                      # If you think that the logs are too much verborse set this to True
    ),
    browser_settings=BrowserSettings(
        browser=Browser.FIREFOX,        # Choose if you want to use Chrome or Firefox as browser
        show=False,                     # Show the browser during bet else headless mode
        do_screenshot=False,            # Do screenshot during the bet
    ),
    bet_settings=BetSettings(
        strategy=Strategy.SMART,        # Choose you strategy!
        percentage=5,                   # Place the x% of your channel points
        percentage_gap=20,              # Gap difference between outcomesA and outcomesB (for SMART stragegy)
        max_points=50000,               # If the x percentage of your channel points is gt bet_max_points set this value
    )
)

twitch_miner.mine(
    ["streamer1", "streamer2"],         # Array of streamers (order = priority)
    followers=False                     # Automatic download the list of your followers
)
```
You can also use all the default values except for your username obv. Short version:
```python
from TwitchChannelPointsMiner import TwitchChannelPointsMiner
twitch_miner = TwitchChannelPointsMiner("your-twitch-username")
twitch_miner.mine(["streamer1", "streamer2"])                   # Array of streamers OR
twitch_miner.mine(followers=True)                               # Automatic use the followers list OR
twitch_miner.mine(["streamer1", "streamer2"], followers=True)   # Mixed
```
4. Start mining! `python run.py`

### Limits
> Twitch has a limit - you can't watch more than 2 channels at one time. We take the first two streamers from the list as they have the highest priority.

Make sure to write the streamers array in order of priority from left to right. If you use `followers=True` Twitch return the streamers order by followed_at. So your last follow have the highest priority.

If the browser are currently betting or wait for more data It's impossible to interact with another event prediction from another streamer.

### Bet strategy

- **MOST_VOTED**: Select the option most voted based on users count
- **HIGH_ODDS**: Select the option with the highest odds
- **PERCENTAGE**: Select the option with the highest percentage based on odds (It's the same that show Twitch) - Should be the same of select LOWEST_ODDS
- **SMART**: If the majority in percent chose an option then follow the other users, otherwise choose the option with the highest odds

![Screenshot](./assets/prediction.png)

Here a concrete example:

- **MOST_VOTED**: 21 Users have select **'over 7.5'**, instead of 9 'under 7.5'
- **HIGH_ODDS**: The highest odd is 2.27 on **'over 7.5'** vs 1.79 on 'under 7.5'
- **PERCENTAGE**: The highest percentage is 56% for **'under 7.5'**
- **SMART**: Calculate the percentage based on the users. The percentage are: 'over 7.5': 70% and 'under 7.5': 30%. If the difference between the two percatage are highter thant `percentage_gap` select the highest percentage, else the highest odds.
In this case if percentage_gap = 20 ; 70-30 = 40 > percentage_gap, so the bot will select 'over 7.5'

## Migrating from old repository (the original one):
If you already have a `twitch-cookies.pkl` and you don't want to login again please create a `cookies/` folder in the current directory and then copy the .pkl file with a new name `your-twitch-username.pkl`
```
.
+-- run.py
+-- cookies
|   +-- your-twitch-username.pkl
```

## Windows
Other users have find multiple problems on Windows my suggestion are:
 - Stop use Windows :stuck_out_tongue_closed_eyes:
 - Suppress the emoji in logs with `logger_settings=LoggerSettings(emoji=False)`
 - Download the geckodriver from here: https://github.com/mozilla/geckodriver/releases/ and extract in the same folder of this project. For other issue with geckodriver just googling: https://stackoverflow.com/questions/40208051/selenium-using-python-geckodriver-executable-needs-to-be-in-path

Other usefully infos can be founded here: https://github.com/gottagofaster236/Twitch-Channel-Points-Miner/issues/31

## Use Chrome instead Firefox
If you prefer Chrome instead Firefox please download the WebDriver matching with your Chrome version and OS from this link: https://chromedriver.chromium.org/downloads.
Extract the archivie, copy the chromedriver file in this project folder.
Edit your run.py file and the browser_settings should something like this:
```python
browser_settings=BrowserSettings(
    browser=Browser.CHROME,
    driver_path="/path/of/your/chromedriver"  # If no path was provided the script will try to search automatically
),
```

## Issue / Debug
When you open a new issue please use the correct template.
Please provide at least the following information/files:
- Browser (if you have the prediction feature enabled)
- Operation System
- Python Version
- logs/ `LoggerSettings(file_level=logging.DEBUG)`
- htmls/ `BrowserSettings(save_html=True)`
- screenshots/ `BrowserSettings(do_screenshot=True)`

Make sure also to have the latest commit.

## Disclaimer
This project comes with no gurantee or warranty. You are responsible for whatever happens from using this project. It is possible to get soft or hard banned by using this project if you are not careful. This is a personal project and is in no way affiliated with Twitch.
