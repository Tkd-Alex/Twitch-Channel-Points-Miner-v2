import copy
import logging
from enum import Enum, auto
from random import uniform

from millify import millify

from TwitchChannelPointsMiner.utils import char_decision_as_index, float_round

logger = logging.getLogger(__name__)


class Strategy(Enum):
    MOST_VOTED = auto()
    HIGH_ODDS = auto()
    PERCENTAGE = auto()
    SMART = auto()

    def __str__(self):
        return self.name


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
    # TOTAL_ and DECISION refer to same key / values
    # But we have different name for help us in filter
    DECISION_USERS = "total_users"
    DECISION_POINTS = "total_points"


class FilterCondition(object):
    def __init__(self, by=None, where=None, value=None, decision=None):
        self.by = by
        self.where = where
        self.value = value

    def __repr__(self):
        return f"FilterCondition(By={self.by}, Where={self.where}, Value={self.value})"


class BetSettings(object):
    def __init__(
        self,
        strategy: Strategy = None,
        percentage: int = None,
        percentage_gap: int = None,
        max_points: int = None,
        stealth_mode: bool = None,
        filter_condition: FilterCondition = None,
    ):
        self.strategy = strategy
        self.percentage = percentage
        self.percentage_gap = percentage_gap
        self.max_points = max_points
        self.stealth_mode = stealth_mode
        self.filter_condition = filter_condition

    def default(self):
        self.strategy = self.strategy if not None else Strategy.SMART
        self.percentage = self.percentage if not None else 5
        self.percentage_gap = self.percentage_gap if not None else 20
        self.max_points = self.max_points if not None else 50000
        self.stealth_mode = self.stealth_mode if not None else False

    def __repr__(self):
        return f"BetSettings(Strategy={self.strategy}, Percentage={self.percentage}, PercentageGap={self.percentage_gap}, MaxPoints={self.max_points}, StealthMode={self.stealth_mode})"


class Bet(object):
    def __init__(self, outcomes: list, settings: BetSettings):
        self.outcomes = outcomes
        self.__clear_outcomes()
        self.decision: dict = {}
        self.total_users = 0
        self.total_points = 0
        self.settings = settings

    def update_outcomes(self, outcomes):
        for index in range(0, len(self.outcomes)):
            self.outcomes[index][OutcomeKeys.TOTAL_USERS] = int(
                outcomes[index][OutcomeKeys.TOTAL_USERS]
            )
            self.outcomes[index][OutcomeKeys.TOTAL_POINTS] = int(
                outcomes[index][OutcomeKeys.TOTAL_POINTS]
            )
            if outcomes[index]["top_predictors"] != []:
                # Sort by points placed by other users
                outcomes[index]["top_predictors"] = sorted(
                    outcomes[index]["top_predictors"],
                    key=lambda x: x["points"],
                    reverse=True,
                )
                # Get the first elements (most placed)
                top_points = outcomes[index]["top_predictors"][0]["points"]
                self.outcomes[index][OutcomeKeys.TOP_POINTS] = top_points

        self.total_users = (
            self.outcomes[0][OutcomeKeys.TOTAL_USERS]
            + self.outcomes[1][OutcomeKeys.TOTAL_USERS]
        )
        self.total_points = (
            self.outcomes[0][OutcomeKeys.TOTAL_POINTS]
            + self.outcomes[1][OutcomeKeys.TOTAL_POINTS]
        )

        if (
            self.total_users > 0
            and self.outcomes[0][OutcomeKeys.TOTAL_POINTS] > 0
            and self.outcomes[1][OutcomeKeys.TOTAL_POINTS] > 0
        ):
            for index in range(0, len(self.outcomes)):
                self.outcomes[index][OutcomeKeys.PERCENTAGE_USERS] = float_round(
                    (100 * self.outcomes[index][OutcomeKeys.TOTAL_USERS])
                    / self.total_users
                )
                self.outcomes[index][OutcomeKeys.ODDS] = float_round(
                    self.total_points / self.outcomes[index][OutcomeKeys.TOTAL_POINTS]
                )
                self.outcomes[index][OutcomeKeys.ODDS_PERCENTAGE] = float_round(
                    100 / self.outcomes[index][OutcomeKeys.ODDS]
                )

        self.__clear_outcomes()

    def __repr__(self):
        return f"Bet(TotalUsers={millify(self.total_users)}, TotalPoints={millify(self.total_points)}), Decision={self.decision})\n\t\tOutcome0({self.get_outcome(0)})\n\t\tOutcome1({self.get_outcome(1)})"

    def get_outcome(self, index):
        outcome = self.outcomes[index]
        return f"{outcome['title']} ({outcome['color']}), Points: {millify(outcome[OutcomeKeys.TOTAL_POINTS])}, Users: {millify(outcome[OutcomeKeys.TOTAL_USERS])} ({outcome[OutcomeKeys.PERCENTAGE_USERS]}%), Odds: {outcome[OutcomeKeys.ODDS]} ({outcome[OutcomeKeys.ODDS_PERCENTAGE]}%)"

    def __clear_outcomes(self):
        for index in range(0, len(self.outcomes)):
            keys = copy.deepcopy(list(self.outcomes[index].keys()))
            for key in keys:
                if key not in [
                    OutcomeKeys.TOTAL_USERS,
                    OutcomeKeys.TOTAL_POINTS,
                    OutcomeKeys.TOP_POINTS,
                    OutcomeKeys.PERCENTAGE_USERS,
                    OutcomeKeys.ODDS,
                    OutcomeKeys.ODDS_PERCENTAGE,
                    "title",
                    "color",
                    "id",
                ]:
                    del self.outcomes[index][key]
            for key in [
                OutcomeKeys.PERCENTAGE_USERS,
                OutcomeKeys.ODDS,
                OutcomeKeys.ODDS_PERCENTAGE,
                OutcomeKeys.TOP_POINTS,
            ]:
                if key not in self.outcomes[index]:
                    self.outcomes[index][key] = 0

    def __return_choice(self, key) -> str:
        return "A" if self.outcomes[0][key] > self.outcomes[1][key] else "B"

    def skip(self) -> bool:
        if self.settings.filter_condition is not None:
            # key == by , condition == where
            key = self.settings.filter_condition.by
            condition = self.settings.filter_condition.where
            value = self.settings.filter_condition.value
            compared_value = (
                (self.outcomes[0][key] + self.outcomes[1][key])
                if key in [OutcomeKeys.TOTAL_USERS, OutcomeKeys.TOTAL_POINTS]
                else self.outcomes[char_decision_as_index(self.decision["choice"])][key]
            )

            logger.info(
                f"Filter applied on this bet. Current {key} is {compared_value}, must be {condition} {value}"
            )
            # Check if condition is satisfied
            if condition == Condition.GT:
                if compared_value > value:
                    return False
            elif condition == Condition.LT:
                if compared_value < value:
                    return False
            elif condition == Condition.GTE:
                if compared_value >= value:
                    return False
            elif condition == Condition.LTE:
                if compared_value <= value:
                    return False
            return True  # Else skip the bet
        else:
            return False  # Default don't skip the bet

    def calculate(self, balance: int) -> dict:
        self.decision = {"choice": None, "amount": 0, "id": None}
        if self.settings.strategy == Strategy.MOST_VOTED:
            self.decision["choice"] = self.__return_choice(OutcomeKeys.TOTAL_USERS)
        elif self.settings.strategy == Strategy.HIGH_ODDS:
            self.decision["choice"] = self.__return_choice(OutcomeKeys.ODDS)
        elif self.settings.strategy == Strategy.PERCENTAGE:
            self.decision["choice"] = self.__return_choice(OutcomeKeys.ODDS_PERCENTAGE)
        elif self.settings.strategy == Strategy.SMART:
            difference = abs(
                self.outcomes[0][OutcomeKeys.PERCENTAGE_USERS]
                - self.outcomes[1][OutcomeKeys.PERCENTAGE_USERS]
            )
            self.decision["choice"] = (
                self.__return_choice(OutcomeKeys.ODDS)
                if difference < self.settings.percentage_gap
                else self.__return_choice(OutcomeKeys.TOTAL_USERS)
            )

        if self.decision["choice"] is not None:
            index = char_decision_as_index(self.decision["choice"])
            self.decision["id"] = self.outcomes[index]["id"]
            self.decision["amount"] = min(
                int(balance * (self.settings.percentage / 100)),
                self.settings.max_points,
            )
            if (
                self.settings.stealth_mode is True
                and self.decision["amount"]
                >= self.outcomes[index][OutcomeKeys.TOP_POINTS]
            ):
                reduce_amount = uniform(1, 5)
                self.decision["amount"] = (
                    self.outcomes[index][OutcomeKeys.TOP_POINTS] - reduce_amount
                )
        return self.decision
