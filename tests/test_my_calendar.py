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


"""
Frst test the first week of a month that starts on Saturday: November 2020 week 0
Next test the first week of a month that starts on a Monday: February 2021 week 0
Next test first week of a month that starts on another day: December 2020 week 0

Test the last week of a month that ends on Saturday: April 2023 week 4
Test the last week of a month that ends on Monday: November 2020 week 5

Test a random week in the middle of a month: November 2020 week 2
"""
@pytest.mark.parametrize(('year', 'month', 'week', 'expected_dates'), (
    (2020, 11, 0, [0, 0, 0, 0, 0, 0, 1]),
    (2021, 2, 0, [1, 2, 3, 4, 5, 6, 7]),
    (2020, 12, 0, [0, 1, 2, 3, 4, 5, 6]),
    (2023, 4, 4, [24, 25, 26, 27, 28, 29, 30]),
    (2020, 11, 5, [30, 0, 0, 0, 0, 0, 0]),
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