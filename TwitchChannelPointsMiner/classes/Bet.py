import logging

from enum import Enum, auto

logger = logging.getLogger(__name__)


class Strategy(Enum):
    MOST_VOTED = auto()
    HIGH_ODDS = auto()
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
            self.outcomes[0]["percentage_users"] = round(
                float((100 * self.outcomes[0]["total_users"]) / self.total_users), 2
            )
            self.outcomes[1]["percentage_users"] = round(
                float((100 * self.outcomes[1]["total_users"]) / self.total_users), 2
            )

            self.outcomes[0]["odds"] = round(
                float(self.total_points / self.outcomes[0]["total_points"]), 2
            )
            self.outcomes[1]["odds"] = round(
                float(self.total_points / self.outcomes[1]["total_points"]), 2
            )

        self.__clear_outcomes()

    def __repr__(self):
        return f"Bet(Outcome0={self.outcomes[0]}, Outcome1={self.outcomes[1]}, TotalUsers={self.total_users}, TotalPoints={self.total_points}), Decision={self.decision})"

    def __clear_outcomes(self):
        for index in range(0, len(self.outcomes)):
            for key in self.outcomes[index]:
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

    def calculate(self, balance: int):
        self.decision = {"choice": "", "amount": 0, "id": None}
        if self.settings.strategy == Strategy.MOST_VOTED:
            self.decision["choice"] = (
                "A"
                if self.outcomes[0]["total_users"] > self.outcomes[1]["total_users"]
                else "B"
            )
        elif self.settings.strategy == Strategy.HIGH_ODDS:
            self.decision["choice"] = (
                "A" if self.outcomes[0]["odds"] > self.outcomes[1]["odds"] else "B"
            )
        elif self.settings.strategy == Strategy.SMART:
            if (
                abs(
                    self.outcomes[0]["percentage_users"]
                    - self.outcomes[1]["percentage_users"]
                )
                < self.settings.percentage_gap
            ):
                self.decision["choice"] = (
                    "A" if self.outcomes[0]["odds"] > self.outcomes[1]["odds"] else "B"
                )
            else:
                self.decision["choice"] = (
                    "A"
                    if self.outcomes[0]["total_users"] > self.outcomes[1]["total_users"]
                    else "B"
                )  # Follow other users

        if self.decision["choice"]:
            self.decision["id"] = (
                self.outcomes[0]["id"]
                if self.decision["choice"] == "A"
                else self.outcomes[1]["id"]
            )
            self.decision["amount"] = min(
                round(balance * (self.settings.percentage / 100)),
                self.settings.max_points,
            )
        return self.decision
