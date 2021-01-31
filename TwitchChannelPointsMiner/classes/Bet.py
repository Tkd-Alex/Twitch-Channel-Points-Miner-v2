import copy
import logging

from enum import Enum, auto

from TwitchChannelPointsMiner.utils import millify
from TwitchChannelPointsMiner.utils import float_round

logger = logging.getLogger(__name__)


class Strategy(Enum):
    MOST_VOTED = auto()
    HIGH_ODDS = auto()
    PERCENTAGE = auto()
    SMART = auto()


class BetSettings:
    def __init__(
        self,
        strategy: Strategy = Strategy.SMART,
        percentage: int = 5,
        percentage_gap: int = 2,
        max_points: int = 50000,
    ):
        self.strategy = strategy
        self.percentage = percentage
        self.percentage_gap = percentage_gap
        self.max_points = max_points

    def __repr__(self):
        return f"BetSettings(Strategy={self.strategy}, Percentage={self.percentage}, PercentageGap={self.percentage_gap}, MaxPoints={self.max_points}"


class Bet:
    def __init__(self, outcomes: list, settings: BetSettings):
        self.outcomes = outcomes
        self.__clear_outcomes()
        self.decision: dict = {}
        self.total_users = 0
        self.total_points = 0
        self.settings = settings

    def update_outcomes(self, outcomes):
        self.outcomes[0]["total_users"] = int(outcomes[0]["total_users"])
        self.outcomes[1]["total_users"] = int(outcomes[1]["total_users"])
        self.outcomes[0]["total_points"] = int(outcomes[0]["total_points"])
        self.outcomes[1]["total_points"] = int(outcomes[1]["total_points"])

        self.total_users = (
            self.outcomes[0]["total_users"] + self.outcomes[1]["total_users"]
        )
        self.total_points = (
            self.outcomes[0]["total_points"] + self.outcomes[1]["total_points"]
        )

        if (
            self.total_users > 0
            and self.outcomes[0]["total_points"] > 0
            and self.outcomes[1]["total_points"] > 0
        ):
            for index in range(0, len(self.outcomes)):
                self.outcomes[index]["percentage_users"] = float_round(
                    (100 * self.outcomes[index]["total_users"]) / self.total_users
                )
                self.outcomes[index]["odds"] = float_round(
                    self.total_points / self.outcomes[index]["total_points"]
                )
                self.outcomes[index]["odds_percentage"] = float_round(
                    100 / self.outcomes[index]["odds"]
                )

        self.__clear_outcomes()

    def __repr__(self):
        return f"Bet(TotalUsers={millify(self.total_users)}, TotalPoints={millify(self.total_points)}), Decision={self.decision})\n\t\tOutcome0({self.get_outcome(0)})\n\t\tOutcome1({self.get_outcome(1)})"

    def get_outcome(self, index):
        outcome = self.outcomes[index]
        return f"{outcome['title']} ({outcome['color']}), Points: {millify(outcome['total_points'])}, Users: {millify(outcome['total_users'])} ({outcome['percentage_users']}%), Odds: {outcome['odds']} ({outcome['odds_percentage']}%)"

    def __clear_outcomes(self):
        for index in range(0, len(self.outcomes)):
            keys = copy.deepcopy(list(self.outcomes[index].keys()))
            for key in keys:
                if key not in [
                    "total_users",
                    "total_points",
                    "percentage_users",
                    "odds",
                    "odds_percentage",
                    "title",
                    "color",
                    "id",
                ]:
                    del self.outcomes[index][key]
            for key in ["percentage_users", "odds", "odds_percentage"]:
                if key not in self.outcomes[index]:
                    self.outcomes[index][key] = 0

    def __return_choice(self, key) -> str:
        return "A" if self.outcomes[0][key] > self.outcomes[1][key] else "B"

    def calculate(self, balance: int) -> dict:
        self.decision = {"choice": None, "amount": 0, "id": None}
        if self.settings.strategy == Strategy.MOST_VOTED:
            self.decision["choice"] = self.__return_choice("total_users")
        elif self.settings.strategy == Strategy.HIGH_ODDS:
            self.decision["choice"] = self.__return_choice("odds")
        elif self.settings.strategy == Strategy.PERCENTAGE:
            self.decision["choice"] = self.__return_choice("odds_percentage")
        elif self.settings.strategy == Strategy.SMART:
            difference = abs(
                self.outcomes[0]["percentage_users"]
                - self.outcomes[1]["percentage_users"]
            )
            self.decision["choice"] = (
                self.__return_choice("odds")
                if difference < self.settings.percentage_gap
                else self.__return_choice("total_users")
            )

        if self.decision["choice"] is not None:
            self.decision["id"] = (
                self.outcomes[0]["id"]
                if self.decision["choice"] == "A"
                else self.outcomes[1]["id"]
            )
            self.decision["amount"] = min(
                int(balance * (self.settings.percentage / 100)),
                self.settings.max_points,
            )
        return self.decision
