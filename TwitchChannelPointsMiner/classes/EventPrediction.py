from TwitchChannelPointsMiner.classes.Bet import Bet, BetSettings
from TwitchChannelPointsMiner.classes.Streamer import Streamer


class EventPrediction:
    def __init__(
        self,
        streamer: Streamer,
        event_id,
        title,
        created_at,
        prediction_window_seconds,
        status,
        outcomes,
        bet_settings: BetSettings = BetSettings()
    ):
        self.streamer = streamer

        self.event_id = event_id
        self.title = title
        self.created_at = created_at
        self.prediction_window_seconds = prediction_window_seconds
        self.status = status
        self.final_result = {}

        self.box_fillable = False
        self.bet_placed = False
        self.bet = Bet(outcomes, bet_settings)

    def __repr__(self):
        return f"EventPrediction(event_id={self.event_id}, title={self.title})"

    def elapsed(self, timestamp):
        return round(float((timestamp - self.created_at).total_seconds()), 2)

    def closing_bet_after(self, timestamp):
        return round(float(self.prediction_window_seconds - self.elapsed(timestamp)), 2)

    def print_recap(self):
        return f"{self} - {self.bet} - {self.final_result}"
