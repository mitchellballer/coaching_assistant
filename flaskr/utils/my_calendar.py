import calendar


class Month:
    # TODO: look into sqlalchemy for storing these objects in my database without a ton of work
    def __init__(self, year, month):
        month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
                       'September', 'October', 'November', 'December']
        self.year = year
        self.month = month
        self.start_day, num_days = calendar.monthrange(year, month)
        self.has_activities = False
        self.weeks = []
        self.month_name = month_names[self.month - 1]
        num_weeks = int(((self.start_day + num_days) / 7) - .001)
        for i in range(num_weeks + 1):
            self.weeks.append(Week(year, month, i))

    def __str__(self):
        return f"there are {len(self.weeks)} weeks in this month"


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