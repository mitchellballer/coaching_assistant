import calendar


class Month:
    # TODO: look into sqlalchemy for storing these objects in my database without a ton of work
    def __init__(self, year, month):
        self.year = year
        self.month = month
        self.start_day, num_days = calendar.monthrange(year, month)
        self.has_activities = False
        self.weeks = []
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
        count = 1

        if week == 0:
            for i in range(start_day):
                self.days.append(Day(year, month, week, 0))
            for i in range(start_day, 7):
                self.days.append(Day(year, month, week, count))
                count += 1
        else:
            count = (7 - start_day) + (7 * (week - 1))
            while count < count + 7 and count < num_days:
                self.days.append(Day(year, month, week, count))
                count += 1
            #while count < count + 7:
            for i in range(7-count):
                self.days.append(Day(year, month, week, 0))


class Day:
    def __init__(self, year, month, week, day):
        self.year = year
        self.month = month
        self.week = week
        self.day = day

