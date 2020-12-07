import calendar
from datetime import date

from flaskr.db import get_db


class Month:
    # TODO: look into sqlalchemy for storing these objects in my database without a ton of work
    def __init__(self, year, month):
        month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
                       'September', 'October', 'November', 'December']
        self.year = year
        self.month = month
        self.start_day, self.num_days = calendar.monthrange(year, month)
        self.has_activities = False
        self.weeks = []
        self.month_name = month_names[self.month - 1]
        num_weeks = int(((self.start_day + self.num_days) / 7) - .001)
        for i in range(num_weeks + 1):
            self.weeks.append(Week(year, month, i))

    def __str__(self):
        return f"there are {len(self.weeks)} weeks in this month"

    def add_activities(self, athlete_id):
        """Add activities that are already in the database for this athlete to this Month"""
        month_start = date(self.year, self.month, 1).isoformat()[:10]
        month_end = date(self.year, self.month, self.num_days).isoformat()[:10]
        db = get_db()
        activities = db.execute(
            'SELECT id, title, description, start_date, distance, duration, athlete_id'
            ' FROM activity'
            ' WHERE athlete_id = ? AND start_date BETWEEN ? AND ?',
            (athlete_id, month_start, month_end,)
        ).fetchall()
        print(month_end)
        for activity in activities:
            # TODO: this is a hacked solution it's almost comical.
            # first 10 characters of start_date are YYYY-MM-DD which is what we need for date object
            self.get_day(activity['start_date'].day).add_activity(activity)

    def get_day(self, day):
        day += self.start_day
        week = int((day / 7) - .001)
        day = (day - 1) % 7
        return self.weeks[week].days[day]


class Week:
    def __init__(self, year, month, week):
        self.year = year
        self.month = month
        self.week = week
        start_day, num_days = calendar.monthrange(year, month)
        self.days = []
        date = 1

        if week == 0:
            for i in range(start_day):
                self.days.append(Day(year, month, week, 0))
            for i in range(start_day, 7):
                self.days.append(Day(year, month, week, date))
                date += 1
        else:
            date = (8 - start_day) + (7 * (week - 1))
            while len(self.days) < 7 and date <= num_days:
                self.days.append(Day(year, month, week, date))
                date += 1
            while len(self.days) < 7:
                self.days.append(Day(year, month, week, 0))


class Day:
    def __init__(self, year, month, week, date):
        self.year = year
        self.month = month
        self.week = week
        self.date = date
        self.activities = []

    def add_activity(self, activity):
        self.activities.append(activity)

    def has_activities(self):
        return len(self.activities) > 0