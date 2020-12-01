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