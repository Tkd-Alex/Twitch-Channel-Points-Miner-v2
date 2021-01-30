from TwitchChannelPointsMiner.classes.entities.Bet import Bet, BetSettings
from TwitchChannelPointsMiner.classes.entities.Streamer import Streamer
from TwitchChannelPointsMiner.utils import float_round


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
        bet_settings: BetSettings,
        less_printing: bool = False,
    ):
        self.streamer = streamer

        self.event_id = event_id
        self.title = title.strip()
        self.created_at = created_at
        self.prediction_window_seconds = prediction_window_seconds
        self.status = status
        self.final_result: dict = {}

        self.box_fillable = False
        self.bet_confirmed = False
        self.bet_placed = False
        self.bet = Bet(outcomes, bet_settings)

        self.less_printing = less_printing

    def __repr__(self):
        return (
            f"EventPrediction: {self.title}"
            if self.less_printing is True
            else f"EventPrediction(event_id={self.event_id}, title={self.title})"
        )

    def __str__(self):
        return (
            f"EventPrediction: {self.title}"
            if self.less_printing is True
            else f"EventPrediction(event_id={self.event_id}, title={self.title})"
        )

    def elapsed(self, timestamp):
        return float_round((timestamp - self.created_at).total_seconds())

    def closing_bet_after(self, timestamp):
        return float_round(self.prediction_window_seconds - self.elapsed(timestamp))

    def print_recap(self) -> str:
        return f"{self}\n\t\t{self.streamer}\n\t\t{self.bet}\n\t\tResult: {self.final_result}"

    def set_less_printing(self, value):
        self.less_printing = value
        self.streamer.less_printing = value
