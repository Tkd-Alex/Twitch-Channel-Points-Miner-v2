import logging
import copy

from enum import Enum, auto

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


def float_round(value):
    return round(float(value), 2)


class Bet:
    def __init__(self, outcomes: list, settings: BetSettings):
        self.outcomes = outcomes
        self.__clear_outcomes()
        self.decision = None
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
            self.outcomes[0]["percentage_users"] = float_round(
                (100 * self.outcomes[0]["total_users"]) / self.total_users
            )
            self.outcomes[1]["percentage_users"] = float_round(
                (100 * self.outcomes[1]["total_users"]) / self.total_users
            )

            self.outcomes[0]["odds"] = float_round(
                self.total_points / self.outcomes[0]["total_points"]
            )
            self.outcomes[1]["odds"] = float_round(
                self.total_points / self.outcomes[1]["total_points"]
            )

            self.outcomes[0]["odds_percetange"] = float_round(
                100 / self.outcomes[0]["odds"]
            )
            self.outcomes[1]["odds_percetange"] = float_round(
                100 / self.outcomes[1]["odds"]
            )

        self.__clear_outcomes()

    def __repr__(self):
        return f"Bet(TotalUsers={self.total_users}, TotalPoints={self.total_points}), Decision={self.decision})\n\t\tOutcome0({self.outcomes[0]})\n\t\tOutcome1({self.outcomes[1]})"

    def __clear_outcomes(self):
        for index in range(0, len(self.outcomes)):
            keys = copy.deepcopy(list(self.outcomes[index].keys()))
            for key in keys:
                if key not in [
                    "total_users",
                    "total_points",
                    "percentage_users",
                    "odds",
                    "title",
                    "color",
                    "id",
                ]:
                    del self.outcomes[index][key]

    def __return_choice(self, key):
        return "A" if self.outcomes[0][key] > self.outcomes[1][key] else "B"

    def calculate(self, balance: int):
        self.decision = {"choice": "", "amount": 0, "id": None}
        if self.settings.strategy == Strategy.MOST_VOTED:
            self.decision["choice"] = self.__return_choice("total_users")
        elif self.settings.strategy == Strategy.HIGH_ODDS:
            self.decision["choice"] = self.__return_choice("odds")
        elif self.settings.strategy == Strategy.PERCENTAGE:
            self.decision["choice"] = self.__return_choice("odds_percetange")
        elif self.settings.strategy == Strategy.SMART:
            difference = abs(self.outcomes[0]["percentage_users"] - self.outcomes[1]["percentage_users"])
            self.decision["choice"] = (
                self.__return_choice("odds")
                if difference < self.settings.percentage_gap
                else self.__return_choice("total_users")
            )

        if self.decision["choice"] != "":
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
