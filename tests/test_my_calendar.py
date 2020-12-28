import pytest
from flaskr.utils.my_calendar import Month, Week, Day

"""
November 2020 starts on Sunday. datetime weeks start on Monday
So this test month needs 6 weeks. We will test Weeks below
[0, 0, 0, 0, 0, 0, 1]
[2, 3, 4, 5, 6, 7, 8]
[9, 10, 11, 12, 13, 14, 15]
[16, 17, 18, 19, 20, 21, 22]
[23, 24, 25, 26, 27, 28, 29]
[30, 0, 0, 0, 0, 0, 0]

April 2023 starts on Saturday. It needs 5 weeks
this month needs 5 weeks
[0, 0, 0, 0, 0, 1, 2]
[3, 4, 5, 6, 7, 8, 9]
[10, 11, 12, 13, 14, 15, 16]
[17, 18, 19, 20, 21, 22, 23]
[24, 25, 26, 27, 28, 29, 30]
"""
@pytest.mark.parametrize(('year', 'month', 'num_weeks', 'start_day'), (
    (2020, 11, 6, 6),
    (2023, 4, 5, 5),
))
def test_month_init(year, month, num_weeks, start_day):
    test = Month(year, month)
    assert len(test.weeks) == num_weeks
    assert test.year == year
    assert test.month == month
    assert test.start_day == start_day  # starts on Saturday
    assert not test.has_activities
    assert isinstance(test.weeks[0], Week)
    assert isinstance(test.weeks[0].days[0], Day)

@pytest.mark.parametrize(('year', 'month', 'day'), (
        (2020, 11, 1), (2020, 11, 2), (2020, 11, 30), (2023, 4, 1), (2023, 4, 2),
        (2023, 4, 3), (2023, 4, 5), (2023, 4, 9),(2023, 4, 24), (2023, 4, 30)
))
def test_get_day(year, month, day):
    test = Month(year, month)
    assert test.get_day(day).date == day

@pytest.mark.parametrize(('year', 'month', 'athlete_id'), (
        (2020, 11, 1),
))
def test_month_add_activities(auth, year, month, athlete_id):
    test = Month(year, month)
    auth.login()

    test.add_activities(athlete_id)

@pytest.mark.parametrize(('year', 'month', 'expected'), (
    (2020, 12, [2020, 11]),
    (2020, 1, [2019, 12]),
))
def test_month_prev_month(year, month, expected):
    test = Month(year, month)
    assert expected == test.prev_month()

@pytest.mark.parametrize(('year', 'month', 'expected'), (
    (2020, 12, [2021, 1]),
    (2020, 1, [2020, 2]),
    (2020, 2, [2020, 3])
))
def test_month_next_month(year, month, expected):
    test = Month(year, month)
    assert expected == test.next_month()


"""
Frst test the first week of a month that starts on Saturday: November 2020 week 0
Next test the first week of a month that starts on a Monday: February 2021 week 0
Next test first week of a month that starts on another day: December 2020 week 0

Test the last week of a month that ends on Saturday: April 2023 week 4
Test the last week of a month that ends on Monday: November 2020 week 5

Test a random week in the middle of a month: November 2020 week 2
"""
@pytest.mark.parametrize(('year', 'month', 'week', 'expected_dates'), (
    (2020, 11, 0, [26, 27, 28, 29, 30, 31, 1]),
    (2021, 2, 0, [1, 2, 3, 4, 5, 6, 7]),
    (2020, 12, 0, [30, 1, 2, 3, 4, 5, 6]),
    (2023, 4, 4, [24, 25, 26, 27, 28, 29, 30]),
    (2020, 11, 5, [30, 1, 2, 3, 4, 5, 6]),
    (2020, 11, 2, [9, 10, 11, 12, 13, 14, 15]),
))
def test_week_innit(year, month, week, expected_dates):
    test = Week(year, month, week)
    assert test.year == year
    assert test.month == month
    assert test.week == week
    assert len(test.days) == 7
    for i in range(7):
        assert test.days[i].date == expected_dates[i]
        if week == 0 and expected_dates[i] > 7:
            assert test.days[i].last_month
        elif week > 2 and expected_dates[i] < 7:
            assert test.days[i].next_month
        else:
            assert not test.days[i].next_month
            assert not test.days[i].last_month

@pytest.mark.parametrize(('year', 'month', 'week', 'expected', 'alternate'), (
    (2020, 12, 0, [2020, 11, 4], [2020, 11, 4]),
    (2020, 12, 1, [2020, 11, 5], [2020, 12, 0]),
    (2020, 1, 1, [2019, 12, 5], [2020, 1, 0]),
    (2020, 1, 0, [2019, 12, 5], [2019, 12, 4]),
    (2020, 2, 1, [2020, 1, 4], [2020, 2, 0]),
    (2020, 2, 2, [2020, 2, 1], [2020, 2, 1]),
    (2020, 2, 3, [2020, 2, 2], [2020, 2, 2]),
    (2020, 2, 4, [2020, 2, 3], [2020, 2, 3]),
))
def test_week_prev_week(year, month, week, expected, alternate):
    test = Week(year, month, week)
    assert expected == test.prev_week() or alternate == test.prev_week()

@pytest.mark.parametrize(('year', 'month', 'week', 'expected', 'alternate'), (
    (2020, 12, 0, [2020, 12, 1], [2020, 12, 1]),
    (2020, 12, 1, [2020, 12, 2], [2020, 12, 2]),
    (2020, 1, 1, [2020, 1, 2], [2020, 1, 2]),
    (2020, 2, 4, [2020, 3, 0], [2020, 3, 0]),
    (2020, 12, 4, [2021, 1, 0], [2021, 1, 0])
))
def test_week_next_week(year, month, week, expected, alternate):
    test = Week(year, month, week)
    assert expected == test.next_week() or alternate == test.next_week()
