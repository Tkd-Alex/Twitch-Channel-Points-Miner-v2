import logging

from enum import Enum, auto

logger = logging.getLogger(__name__)


class Strategy(Enum):
    MOST_VOTED = auto()
    HIGH_COTE = auto()
    SMART = auto()


class Bet:
    def __init__(self, outcomes):
        self.outcomes = outcomes
        self.__clear_outcomes()
        self.total_users = 0
        self.total_points = 0

    def update_outcomes(self, outcomes):
        self.outcomes[0]["total_users"] = int(outcomes[0]["total_users"])
        self.outcomes[1]["total_users"] = int(outcomes[1]["total_users"])
        self.outcomes[0]["total_points"] = int(outcomes[0]["total_points"])
        self.outcomes[1]["total_points"] = int(outcomes[1]["total_points"])

        self.total_users = self.outcomes[0]["total_users"] + self.outcomes[1]["total_users"]
        self.total_points = self.outcomes[0]["total_points"] + self.outcomes[1]["total_points"]

        if (self.total_users > 0 and self.outcomes[0]["total_points"] > 0 and self.outcomes[1]["total_points"] > 0):
            self.outcomes[0]["percentage_users"] = round(float((100 * self.outcomes[0]["total_users"]) / self.total_users), 2)
            self.outcomes[1]["percentage_users"] = round(float((100 * self.outcomes[1]["total_users"]) / self.total_users), 2)

            self.outcomes[0]["cote"] = round(float(self.total_points / self.outcomes[0]["total_points"]), 2)
            self.outcomes[1]["cote"] = round(float(self.total_points / self.outcomes[1]["total_points"]), 2)

        self.__clear_outcomes()

    def __repr__(self):
        return f"Bet(Outcome0={self.outcomes[0]}, Outcome1={self.outcomes[1]}, total_users={self.total_users}, total_points={self.total_points})"

    def __clear_outcomes(self):
        for index in range(0, len(self.outcomes)):
            for key in self.outcomes[index]:
                if key not in ["total_users", "total_points", "percentage_users", "cote", "title", "color", "id"]:
                    del self.outcomes[index][key]

    def calculate(self, balance: int, strategy: Strategy = Strategy.SMART, percentage=5, percentage_gap=20, max_points=50000):
        output = {"choice": "", "amount": 0, "id": None}

        if strategy == Strategy.MOST_VOTED:
            output['choice'] = "A" if self.outcomes[0]["total_users"] > self.outcomes[1]["total_users"] else "B"
        elif strategy == Strategy.HIGH_COTE:
            output['choice'] = "A" if self.outcomes[0]["cote"] > self.outcomes[1]["cote"] else "B"
        elif strategy == Strategy.SMART:
            difference_percentage = (self.outcomes[0]["percentage_users"] - self.outcomes[1]["percentage_users"]) if self.outcomes[0]["percentage_users"] > self.outcomes[1]["percentage_users"] else (self.outcomes[1]["percentage_users"] - self.outcomes[0]["percentage_users"])
            if difference_percentage < percentage_gap:
                output['choice'] = "A" if self.outcomes[0]["cote"] > self.outcomes[1]["cote"] else "B"
            else:
                output['choice'] = "A" if self.outcomes[0]["total_users"] > self.outcomes[1]["total_users"] else "B"   # Follow other users

        if output['choice']:
            output['id'] = self.outcomes[0]["id"] if output['choice'] == "A" else self.outcomes[1]["id"]
            output['amount'] = min(round(balance * (percentage / 100)), max_points)
        return output
