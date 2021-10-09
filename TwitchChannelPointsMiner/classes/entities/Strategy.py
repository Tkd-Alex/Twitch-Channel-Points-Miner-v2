import logging
from enum import Enum, auto
from random import uniform

from TwitchChannelPointsMiner.classes.Settings import Settings
from TwitchChannelPointsMiner.utils import char_decision_as_index

logger = logging.getLogger(__name__)


class Condition(Enum):
    GT = auto()
    LT = auto()
    GTE = auto()
    LTE = auto()

    def __str__(self):
        return self.name


class OutcomeKeys(object):
    # Real key on Bet dict ['']
    PERCENTAGE_USERS = "percentage_users"
    ODDS_PERCENTAGE = "odds_percentage"
    ODDS = "odds"
    TOP_POINTS = "top_points"
    # Real key on Bet dict [''] - Sum()
    TOTAL_USERS = "total_users"
    TOTAL_POINTS = "total_points"
    # This key does not exist
    DECISION_USERS = "decision_users"
    DECISION_POINTS = "decision_points"


class Strategy(object):
    MOST_VOTED = "MostVoted"
    HIGH_ODDS = "HighOdds"
    SMART_HIGH_ODDS = "SmartHighOdds"
    PERCENTAGE = "Percentage"
    SMART = "Smart"

    def __init__(self, outcomes: list, settings: object):
        self.outcomes = outcomes
        self.decision: dict = {}
        self.settings = settings

    def get_instance(self):
        subclass = globals()[self.settings.strategy]
        return subclass(self.outcomes, self.settings)

    def return_choice(self, key) -> str:
        return "A" if self.outcomes[0][key] > self.outcomes[1][key] else "B"

    def calculate_before(self):
        self.decision = {"choice": None, "amount": 0, "id": None}

    def calculate_middle(self):
        pass

    def calculate_after(self, balance: int):
        if self.settings.only_doubt:
            self.decision["choice"] = "B"
        if self.decision["choice"] is not None:
            index = char_decision_as_index(self.decision["choice"])
            self.decision["id"] = self.outcomes[index]["id"]
            amounts = [
                self.decision["amount"],
                int(balance * (self.settings.percentage / 100)),
                self.settings.max_points,
            ]
            self.decision["amount"] = min(x for x in amounts if x != 0)
            if (
                self.settings.stealth_mode is True
                and self.decision["amount"]
                >= self.outcomes[index][OutcomeKeys.TOP_POINTS]
            ):
                reduce_amount = uniform(1, 5)
                self.decision["amount"] = (
                    self.outcomes[index][OutcomeKeys.TOP_POINTS] - reduce_amount
                )
            self.decision["amount"] = int(self.decision["amount"])

    def calculate(self, balance: int) -> dict:
        self.calculate_before()
        self.calculate_middle()
        self.calculate_after(balance)
        return self.decision

    def skip_before(self):
        pass

    def skip_middle(self):
        pass

    def skip_after(self):
        if self.settings.filter_condition is not None:
            self.decision.setdefault("choice", None)  # for tests
            # key == by , condition == where
            key = self.settings.filter_condition.by
            condition = self.settings.filter_condition.where
            value = self.settings.filter_condition.value

            fixed_key = (
                key
                if key not in [OutcomeKeys.DECISION_USERS, OutcomeKeys.DECISION_POINTS]
                else key.replace("decision", "total")
            )
            if key in [OutcomeKeys.TOTAL_USERS, OutcomeKeys.TOTAL_POINTS]:
                compared_value = (
                    self.outcomes[0][fixed_key] + self.outcomes[1][fixed_key]
                )
            else:
                outcome_index = char_decision_as_index(self.decision["choice"])
                compared_value = self.outcomes[outcome_index][fixed_key]

            # Check if condition is satisfied
            if condition == Condition.GT:
                if compared_value > value:
                    return False, compared_value
            elif condition == Condition.LT:
                if compared_value < value:
                    return False, compared_value
            elif condition == Condition.GTE:
                if compared_value >= value:
                    return False, compared_value
            elif condition == Condition.LTE:
                if compared_value <= value:
                    return False, compared_value
            return True, compared_value  # Else skip the bet
        else:
            return False, 0  # Default don't skip the bet

    def skip(self) -> bool:
        skip_results = [self.skip_before(), self.skip_middle(), self.skip_after()]
        return next(item for item in skip_results if item is not None)

    def __str__(self):
        return self.name


class StrategySettings(object):
    def __init__(self, strategy: Strategy = None, **kwargs):
        subclass = globals()[f"{strategy}Settings"]
        self.instance = subclass(**kwargs)
        self.instance.default()

    def get_instance(self):
        return self.instance


class SmartHighOddsSettings(object):
    __slots__ = [
        "target_odd",
        "always_bet",
    ]

    def __init__(
        self,
        target_odd: float = None,
        always_bet: bool = None,
    ):
        self.target_odd = target_odd
        self.always_bet = always_bet

    def default(self):
        self.target_odd = self.target_odd if self.target_odd is not None else 3
        self.always_bet = self.always_bet if self.always_bet is not None else False


class SmartSettings(object):
    __slots__ = [
        "percentage_gap",
    ]

    def __init__(
        self,
        percentage_gap: float = None,
    ):
        self.percentage_gap = percentage_gap

    def default(self):
        self.percentage_gap = (
            self.percentage_gap if self.percentage_gap is not None else 20
        )


class SmartHighOdds(Strategy):
    def both_odds_too_low(self) -> bool:
        return (
            self.outcomes[0][OutcomeKeys.ODDS]
            <= self.settings.strategy_settings.target_odd
            and self.outcomes[1][OutcomeKeys.ODDS]
            <= self.settings.strategy_settings.target_odd
        )

    def is_only_doubt(self) -> bool:
        return (
            self.outcomes[1][OutcomeKeys.ODDS]
            <= self.settings.strategy_settings.target_odd
            and self.settings.only_doubt
        )

    def log_skip(self, string) -> str:
        logger.info(
            string,
            extra={
                "emoji": ":pushpin:",
                "color": Settings.logger.color_palette.BET_GENERAL,
            },
        )

    def skip_middle(self):
        if self.settings.strategy_settings.always_bet:
            self.log_skip("always_bet activated")
            return False, 0

        if (
            self.outcomes[0][OutcomeKeys.TOTAL_POINTS] > 0
            and self.outcomes[1][OutcomeKeys.TOTAL_POINTS] == 0
        ):
            self.log_skip("No bet on B")
            return False, 0
        if (
            self.outcomes[0][OutcomeKeys.TOTAL_POINTS] == 0
            and self.outcomes[1][OutcomeKeys.TOTAL_POINTS] > 0
        ):
            if not self.settings.only_doubt:
                self.log_skip("No bet on A")
                return False, 0

        if self.both_odds_too_low() or self.is_only_doubt():
            if self.both_odds_too_low():
                self.log_skip("Odd is too low")
            elif self.is_only_doubt():
                self.log_skip("Odd is too low and only_doubt activated")
            self.log_skip(f"Target odd: {self.settings.strategy_settings.target_odd}")
            return True, 0  # Skip

    def calculate_sho_bet(self, index):
        low_odd_points = self.outcomes[1 - index][OutcomeKeys.TOTAL_POINTS]
        high_odd_points = self.outcomes[index][OutcomeKeys.TOTAL_POINTS]
        if self.both_odds_too_low() or self.is_only_doubt():
            return 10
        elif high_odd_points <= 50:  # in case no one bet
            return 50
        else:
            target_odd = self.settings.strategy_settings.target_odd
            if self.outcomes[index][OutcomeKeys.ODDS] > (target_odd * 2):
                # don't bet too much if odds is too high
                target_odd = self.outcomes[index][OutcomeKeys.ODDS] / 2
            return int((low_odd_points / (target_odd - 1)) - high_odd_points)

    def calculate_middle(self):
        self.decision["choice"] = self.return_choice(OutcomeKeys.ODDS)
        if self.decision["choice"] is not None:
            index = char_decision_as_index(self.decision["choice"])
            self.decision["amount"] = int(self.calculate_sho_bet(index))


class MostVoted(Strategy):
    def calculate_middle(self):
        self.decision["choice"] = self.return_choice(OutcomeKeys.TOTAL_USERS)


class HighOdds(Strategy):
    def calculate_middle(self):
        self.decision["choice"] = self.return_choice(OutcomeKeys.ODDS)


class Percentage(Strategy):
    def calculate_middle(self):
        self.decision["choice"] = self.return_choice(OutcomeKeys.ODDS_PERCENTAGE)


class Smart(Strategy):
    def calculate_middle(self):
        difference = abs(
            self.outcomes[0][OutcomeKeys.PERCENTAGE_USERS]
            - self.outcomes[1][OutcomeKeys.PERCENTAGE_USERS]
        )
        self.decision["choice"] = (
            self.return_choice(OutcomeKeys.ODDS)
            if difference < self.settings.strategy_settings.percentage_gap
            else self.return_choice(OutcomeKeys.TOTAL_USERS)
        )
