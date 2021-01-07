import calendar
from datetime import date, timedelta, datetime

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

    # TODO: this functionality should be on the week level. Month.add_activities should tell it's week objects to add_activities
    def add_activities(self, athlete_id):
        """Add activities that are already in the database for this athlete to this Month"""
        for week in self.weeks:
            week.add_activities(athlete_id)
        """
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
        """

    def get_day(self, day):
        """retrieve day object from date of month"""
        day += self.start_day
        week = int((day / 7) - .001)
        day = (day - 1) % 7
        return self.weeks[week].days[day]

    def get_week_from_day(self, day):
        """retrieve week object of month that contains given day of month. """
        day += self.start_day
        week = int((day / 7) - .001)
        return self.weeks[week]

    def get_curr_week(self):
        """retrieve week number of current week"""
        day = datetime.now().day + self.start_day
        week = int((day / 7) - .001)
        return week

    def prev_month(self):
        """return tuple containing year and month of the previous month"""
        curr = datetime(self.year, self.month, 1) - timedelta(days=1)
        return [curr.year, curr.month]

    def next_month(self):
        """return tuple containing year and month of the next month"""
        curr = datetime(self.year, self.month, 28) + timedelta(days=5)
        return [curr.year, curr.month]


class Week:
    def __init__(self, year, month, week):
        self.year = year
        self.month = month
        #this is the number week of the month
        self.week = week
        self.start_day, num_days = calendar.monthrange(year, month)
        self.days = []
        date_count = 1
        next_month_date = 1
        prev_month_date = (date(self.year, self.month, 1) - timedelta(days=self.start_day)).day

        if week == 0:
            for i in range(self.start_day):
                self.days.append(Day(year, month, week, prev_month_date, True, False))
                prev_month_date += 1
            for i in range(self.start_day, 7):
                self.days.append(Day(year, month, week, date_count, False, False))
                date_count += 1
        else:
            date_count = (8 - self.start_day) + (7 * (week - 1))
            while len(self.days) < 7 and date_count <= num_days:
                self.days.append(Day(year, month, week, date_count, False, False))
                date_count += 1
            while len(self.days) < 7:
                self.days.append(Day(year, month, week, next_month_date, False, True))
                next_month_date += 1

    def add_activities(self, athlete_id):
        if self.days[0].last_month:
            week_start = (date(self.year, self.month, 1) - timedelta(days=self.start_day)).isoformat()[:10]
        else:
            week_start = date(self.year, self.month, self.days[0].date).isoformat()[:10]

        if self.days[-1].next_month:
            # the end of the week is the first day of the week plus 7 days (we want the very beginning of the next week for our range)
            week_end = (date(self.year, self.month, self.days[0].date) + timedelta(days=7)).isoformat()[:10]

        else:
            week_end = (date(self.year, self.month, self.days[-1].date) + timedelta(days=1)).isoformat()[:10]

        db = get_db()
        activities = db.execute(
            'SELECT id, title, description, start_date, distance, duration, athlete_id'
            ' FROM activity'
            ' WHERE athlete_id = ? AND start_date BETWEEN ? AND ?',
            (athlete_id, week_start, week_end,)
        ).fetchall()
        for activity in activities:
            # TODO: this is a hacked solution it's almost comical.
            # first 10 characters of start_date are YYYY-MM-DD which is what we need for date object
            self.get_day(activity['start_date'].day).add_activity(activity)

    def get_day(self, day):
        """retrieve Day object who has given date"""
        day += self.start_day
        return self.days[(day - 1) % 7]

    # TODO: make this more elegant. Seems like a terrible solution
    def prev_week(self):
        """return tuple (year, month, week) of the previous week"""
        new_month = self.month
        new_year = self.year
        if self.month == 1:
            new_year = self.year - 1
            new_month = 13
        else:
            new_year = self.year

        if self.week > 0:
            return [self.year, self.month, self.week-1]
        else:
            new_month = new_month - 1
            new_month_start, new_month_len = calendar.monthrange(new_year, new_month)
            new_week = int(((new_month_start + new_month_len) / 7) - .001) - 1
            return [new_year, new_month, new_week]
        """ fancy datetime, timedelta logic is too complicated due to some days in a week given week not belonging to same month
        #make datetime object of the start of this week
        curr = datetime(self.year, self.month, self.days[6].date)
        prev = curr - timedelta(days=7)
        prev_start = calendar.monthrange(prev.year, prev.month)[0]
        week_num = int(((prev.day + prev_start) / 7) - .001)
        return [prev.year, prev.month, week_num]
        """

    def next_week(self):
        """return tuple (year, month, week) of the next week"""
        new_month = self.month
        new_week = self.week + 1
        new_year = self.year
        # if the end of this week is in the next month
        if self.days[-1].next_month and self.month == 12:
            new_week = 0
            new_month = 1
            new_year = self.year + 1 
        elif self.days[-1].next_month:
            new_week = 0
            new_month += 1
        
        return [new_year, new_month, new_week]

class Day:
    def __init__(self, year, month, week, date, last_month, next_month):
        self.year = year
        self.month = month
        self.week = week
        self.date = date
        self.activities = []
        self.last_month = last_month
        self.next_month = next_month

    def add_activity(self, activity):
        self.activities.append(activity)

    def has_activities(self):
        return len(self.activities) > 0

    def miles(self):
        """return today's first activity in miles"""
        return round(self.activities[0]['distance'] / 1609.344,1)