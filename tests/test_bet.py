from TwitchChannelPointsMiner.classes.entities.Bet import (
    Bet,
    Strategy,
    BetSettings,
    Condition,
    OutcomeKeys,
    FilterCondition,
    DelayMode
)
import pytest


@pytest.fixture
def bet_settings():
    settings = BetSettings(
        strategy=Strategy.SMART_HIGH_ODDS,
        percentage=50,
        target_odd=2.1,
        only_doubt=True,
        max_points=50000,
        stealth_mode=False,
        delay_mode=DelayMode.FROM_END,
        delay=6
    )
    return settings


@pytest.fixture
def outcomes():
    outcomes = [
        {
            "percentage_users": 50,
            "odds_percentage": 60,
            "odds": 1.67,
            "top_points": 600,
            "total_users": 1,
            "total_points": 600,
            "decision_users": 1,
            "decision_points": 1,
            "id": 1
        },
        {
            "percentage_users": 50,
            "odds_percentage": 40,
            "odds": 2.5,
            "top_points": 400,
            "total_users": 1,
            "total_points": 400,
            "decision_users": 1,
            "decision_points": 1,
            "id": 2
        }
    ]
    return outcomes


def test_settings(bet_settings, outcomes):
    bet = Bet(outcomes, bet_settings).calculate(1000)
    assert bet["choice"] == "B"
    assert bet["amount"] == 145


def test_settings2(bet_settings, outcomes):
    outcomes[1]["odds"] = 12
    outcomes[0]["odds"] = 1.09
    outcomes[0]["top_points"] = 4400
    outcomes[0]["total_points"] = 4400
    bet = Bet(outcomes, bet_settings).calculate(1000)
    assert bet["amount"] == 480


def test_settings3(bet_settings, outcomes):
    outcomes[1]["odds"] = 13
    outcomes[0]["odds"] = 1.08
    outcomes[1]["top_points"] = 50
    outcomes[1]["total_points"] = 50
    bet = Bet(outcomes, bet_settings).calculate(1000)
    assert bet["amount"] == 50


def test_settings4(bet_settings, outcomes):
    outcomes[1]["odds"] = 2
    outcomes[0]["odds"] = 2
    outcomes[1]["top_points"] = 600
    outcomes[1]["total_points"] = 600
    bet = Bet(outcomes, bet_settings).calculate(1000)
    assert bet["amount"] == 10


def test_settings5(bet_settings, outcomes):
    outcomes = [outcomes[1], outcomes[0]]
    bet_settings.only_doubt = False
    bet = Bet(outcomes, bet_settings).calculate(1000)
    assert bet["choice"] == "A"
    assert bet["amount"] == 145


def test_most_voted(bet_settings, outcomes):
    bet_settings.only_doubt = False
    bet_settings.strategy = Strategy.MOST_VOTED
    bet_settings.percentage = 20
    outcomes[0]["total_users"] = 1
    outcomes[1]["total_users"] = 2
    bet = Bet(outcomes, bet_settings).calculate(1000)
    assert bet["choice"] == "B"
    assert bet["amount"] == 200
    outcomes[0]["total_users"] = 2
    outcomes[1]["total_users"] = 1
    bet = Bet(outcomes, bet_settings).calculate(1000)
    assert bet["choice"] == "A"


def test_high_odds(bet_settings, outcomes):
    bet_settings.only_doubt = False
    bet_settings.strategy = Strategy.HIGH_ODDS
    bet_settings.percentage = 20
    outcomes[0]["odds"] = 2
    outcomes[1]["odds"] = 3
    bet = Bet(outcomes, bet_settings).calculate(1000)
    assert bet["choice"] == "B"
    assert bet["amount"] == 200
    outcomes[0]["odds"] = 3
    outcomes[1]["odds"] = 2
    bet = Bet(outcomes, bet_settings).calculate(1000)
    assert bet["choice"] == "A"


def test_percentage(bet_settings, outcomes):
    bet_settings.only_doubt = False
    bet_settings.strategy = Strategy.PERCENTAGE
    bet_settings.percentage = 20
    outcomes[0]["odds_percentage"] = 2
    outcomes[1]["odds_percentage"] = 3
    bet = Bet(outcomes, bet_settings).calculate(1000)
    assert bet["choice"] == "B"
    assert bet["amount"] == 200
    outcomes[0]["odds_percentage"] = 3
    outcomes[1]["odds_percentage"] = 2
    bet = Bet(outcomes, bet_settings).calculate(1000)
    assert bet["choice"] == "A"


def test_smart(bet_settings, outcomes):
    bet_settings.only_doubt = False
    bet_settings.strategy = Strategy.SMART
    bet_settings.percentage_gap = 1
    outcomes[0]["percentage_users"] = 30
    outcomes[1]["percentage_users"] = 70
    outcomes[0]["total_users"] = 30
    outcomes[1]["total_users"] = 70
    bet = Bet(outcomes, bet_settings).calculate(1000)
    assert bet["choice"] == "B"
    assert bet["amount"] == 500
    outcomes[0]["percentage_users"] = 60
    outcomes[1]["percentage_users"] = 40
    outcomes[0]["total_users"] = 60
    outcomes[1]["total_users"] = 40
    bet = Bet(outcomes, bet_settings).calculate(1000)
    assert bet["choice"] == "A"


def test_smart2(bet_settings, outcomes):
    bet_settings.only_doubt = False
    bet_settings.strategy = Strategy.SMART
    bet_settings.percentage_gap = 99
    outcomes[0]["percentage_users"] = 30
    outcomes[1]["percentage_users"] = 70
    bet = Bet(outcomes, bet_settings).calculate(1000)
    assert bet["choice"] == "B"
    assert bet["amount"] == 500
    outcomes[0]["percentage_users"] = 60
    outcomes[1]["percentage_users"] = 40
    outcomes[0]["odds"] = 2
    outcomes[1]["odds"] = 1
    bet = Bet(outcomes, bet_settings).calculate(1000)
    assert bet["choice"] == "A"


def test_only_doubt(bet_settings, outcomes):
    bet = Bet(outcomes, bet_settings).calculate(1000)
    assert bet["choice"] == "B"
    assert bet["amount"] == 145
    outcomes[1]["odds"] = 2
    bet = Bet(outcomes, bet_settings).calculate(1000)
    assert bet["choice"] == "B"
    assert bet["amount"] == 10


def test_skip(bet_settings, outcomes):
    bet_settings.filter_condition = FilterCondition(
        by=OutcomeKeys.ODDS,
        where=Condition.GT,
        value=2.4
    )
    skip = Bet(outcomes, bet_settings).skip()
    assert skip == (False, 2.5)


def test_skip2(bet_settings, outcomes):
    bet_settings.filter_condition = FilterCondition(
        by=OutcomeKeys.ODDS,
        where=Condition.GT,
        value=2.6
    )
    skip = Bet(outcomes, bet_settings).skip()
    assert skip == (True, 2.5)
