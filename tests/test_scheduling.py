import datetime
import sys

import dateutil.parser
import dateutil.tz
import pytest

from nikola.plugins.command.new_post import get_date

freezegun = pytest.importorskip('freezegun')
freeze_time = freezegun.freeze_time

UTC = dateutil.tz.tzutc()
RULE_TH = 'RRULE:FREQ=WEEKLY;BYDAY=TH'
RULE_FR = 'RRULE:FREQ=WEEKLY;BYDAY=FR'


def test_get_date(today):
    # NOW does not match rule #########################################
    # No last date
    expected = today.replace(day=23)
    assert expected == get_date(True, RULE_FR, tz=UTC)[1]
    assert expected == get_date(True, RULE_FR, tz=UTC)[1]

    # Last date in the past; doesn't match rule
    date = today.replace(hour=7)
    expected = today.replace(day=23, hour=7)
    assert expected == get_date(True, RULE_FR, date, tz=UTC)[1]

    # Last date in the future; doesn't match rule
    date = today.replace(day=24, hour=7)
    expected = today.replace(day=30, hour=7)
    assert expected == get_date(True, RULE_FR, date, tz=UTC)[1]

    # Last date in the past; matches rule
    date = today.replace(day=16, hour=8)
    expected = today.replace(day=23, hour=8)
    assert expected == get_date(True, RULE_FR, date, tz=UTC)[1]

    # Last date in the future; matches rule
    date = today.replace(day=23, hour=18)
    expected = today.replace(day=30, hour=18)
    assert expected == get_date(True, RULE_FR, date, tz=UTC)[1]


def test_current_time_matching_rule(now):
    # NOW matches rule ################################################
    # Not scheduling should return NOW
    assert now == get_date(False, RULE_TH, tz=UTC)[1]

    # No last date
    assert now == get_date(True, RULE_TH, tz=UTC)[1]
    assert now == get_date(True, RULE_TH, tz=UTC)[1]


def test_last_date_in_the_past_not_matching_rule(today):
    # Last date in the past; doesn't match rule
    # Corresponding time has already passed, today
    date = today.replace(day=21, hour=7)
    expected = today.replace(day=29, hour=7)
    assert expected == get_date(True, RULE_TH, date, tz=UTC)[1]
    # Corresponding time has not passed today
    date = today.replace(day=21, hour=18)
    expected = today.replace(day=22, hour=18)
    assert expected == get_date(True, RULE_TH, date, tz=UTC)[1]


def test_last_date_in_the_future_not_matching_rule(today):
    # Last date in the future; doesn't match rule
    # Corresponding time has already passed, today
    date = today.replace(day=24, hour=7)
    expected = today.replace(day=29, hour=7)
    assert expected == get_date(True, RULE_TH, date, tz=UTC)[1]

    # Corresponding time has not passed today
    date = today.replace(day=24, hour=18)
    expected = today.replace(day=29, hour=18)
    assert expected == get_date(True, RULE_TH, date, tz=UTC)[1]


def test_last_date_in_the_past_matching_rule(today):
    # Last date in the past; matches rule
    # Corresponding time has already passed, today
    date = today.replace(day=15, hour=7)
    expected = today.replace(day=29, hour=7)
    assert expected == get_date(True, RULE_TH, date, tz=UTC)[1]

    # Corresponding time has already passed, today; rule specifies HOUR
    date = today.replace(day=15, hour=7)
    expected = today.replace(day=29, hour=9)
    assert expected == get_date(True, RULE_TH + ';BYHOUR=9', date, tz=UTC)[1]

    # Corresponding time has not passed today
    date = today.replace(day=15, hour=18)
    expected = today.replace(day=22, hour=18)
    assert expected == get_date(True, RULE_TH, date, tz=UTC)[1]


def test_last_date_in_the_future_matching_rule(today):
    # Last date in the future; matches rule
    # Corresponding time has already passed, today
    date = today.replace(day=29, hour=7)
    expected = today.replace(day=5, month=9, hour=7)
    assert expected == get_date(True, RULE_TH, date, tz=UTC)[1]

    # Corresponding time has not passed today
    date = today.replace(day=22, hour=18)
    expected = today.replace(day=29, hour=18)
    assert expected == get_date(True, RULE_TH, date, tz=UTC)[1]


@pytest.fixture
def today(now):
    current_time = now.strftime('%Y-%m-%d %H:%M:%S %Z')
    yield dateutil.parser.parse(current_time)


@pytest.fixture
def now() -> datetime:
    """
    Get the current time.

    datetime is frozen to this point in time.
    """
    _NOW = datetime.datetime(2013, 8, 22, 10, 0, 0, tzinfo=UTC)  # Thursday

    with freeze_time(_NOW):
        yield _NOW


@pytest.fixture(autouse=True)
def disable_six_modules():
    deleted = {
        name: sys.modules.pop(name)
        for name in sys.modules
        if name.startswith("six.moves.")
    }
    try:
        yield
    finally:
        for name, mod in deleted.items():
            sys.modules[name] = mod
