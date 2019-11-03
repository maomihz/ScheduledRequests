from datetime import datetime, timedelta

class CronItem:
    ''' Representation of a cron expression element '''
    __slots__ = ('low', 'high', 'every', 'any', 'limit_min', 'limit_max', 'replacement')

    def __init__(self, itemexpr, limit_min=None, limit_max=None, replacement=dict()):
        self.every = 1     # Interval
        self.any = False   # Match *

        # Lower and higher range
        self.low = limit_min or 0
        self.high = limit_max

        # Minimal and maximum allowed
        self.limit_min = limit_min
        self.limit_max = limit_max

        # Equivalency, key -> value: key is replaced to value
        # Can be used for month replacement (jan -> 1)
        # or day of week replacement (sun -> 0)
        # String must be lowercase
        self.replacement = replacement

        self.__parse(itemexpr)

    def match(self, now):
        ''' Test if a given number matches the cron expression

        A given number matches the cron expression when the following condition holds:
            1. The number falls within the range. Either * or [low, high]
            2. The number matches given interval.
                Choose from low, low + every, low + 2 * every ...
        '''
        return (self.any or (now >= self.low and now <= self.high)) \
            and (now - self.low) % self.every == 0

    def __parse(self, expr):
        ''' Parse cron expression and assign correct value for low, high, every '''
        subexpr = expr
        if '/' in expr:
            subexpr, every = expr.split('/', 1)
            if not every.isdigit():
                raise ValueError("Invalid interval: %s in expression %s" % (every, expr))
            self.every = int(every)

        if subexpr == '*':
            self.any = True
            return

        if '-' in subexpr:
            L, R = subexpr.split('-', 1)
        else:
            L, R = subexpr, subexpr

        if L:
            self.low = self.__check_range(L)
        if R:
            self.high = self.__check_range(R)

        if self.low > self.high:
            raise ValueError("Invalid range value: %d-%d" % (self.low, self.high))

    def __check_range(self, value):
        ''' Convert string to integer and check for validity

        The function do the following things:
            1. For a string, convert to lowercase and replace it with an integer
            2. Check if the integer falls within the [limit_min, limit_max] range
            3. Do another replacement for the integer
        '''
        # Convert to integer
        if type(value) is str:
            # string replacement
            if value.lower() in self.replacement:
                value = self.replacement[value.lower()]
            else:
                if not value.isdigit():
                    raise ValueError("Invalid integer: %s" % value)
                value = int(value)

        # Check range
        if (self.limit_min != None and value < self.limit_min) or (self.limit_max != None and value > self.limit_max):
            raise ValueError("Value not allowed: %d (in: %d - %d)" % (value, self.limit_min, self.limit_max))

        # integer replacement
        return self.replacement.get(value, value)


    def __str__(self):
        ''' Return a valid crontab expression element '''
        pattern = []
        if self.any:
            pattern.append('*')
        elif self.low == self.high:
            pattern.append('%d' % self.low)
        else:
            pattern.append('%d-%d' % (self.low, self.high))

        if self.every != 1:
            pattern.append('/%d' % self.every)

        return ''.join(pattern)


class CronTab:
    ''' Representation of a cron expression '''

    months = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr': 4,
        'may': 5,
        'jun': 6,
        'jul': 7,
        'aug': 8,
        'sep': 9,
        'oct': 10,
        'nov': 11,
        'dec': 12
    }

    weekdays = {
        'mon': 1,
        'tue': 2,
        'wed': 3,
        'thu': 4,
        'fri': 5,
        'sat': 6,
        'sun': 0,
        7: 0 # Allow 7 as sunday
    }

    __slots__ = ('m', 'h', 'd', 'M', 'D')

    def __init__(self, cronexpr):
        m, h, d, M, D = cronexpr.split()[:5]

        # minute hour day month day-of-week
        self.m = [CronItem(x, 0, 59) for x in m.split(',')]
        self.h = [CronItem(x, 0, 23) for x in h.split(',')]
        self.d = [CronItem(x, 1, 31) for x in d.split(',')]
        self.M = [CronItem(x, 1, 12, replacement=self.months) for x in M.split(',')]
        self.D = [CronItem(x, 0, 7, replacement=self.weekdays) for x in D.split(',')]

    def is_now(self, dt=None):
        ''' Check if the cron expression matches current time '''
        if not dt:
            dt = datetime.now()
        weekday = (dt.weekday() + 1) % 7

        return all((
            any(x.match(dt.minute) for x in self.m),
            any(x.match(dt.hour) for x in self.h),
            any(x.match(dt.day) for x in self.d),
            any(x.match(dt.month) for x in self.M),
            any(x.match(weekday) for x in self.D),
        ))


    def __str__(self):
        return ' '.join(
            ','.join(str(x) for x in cron)
            for cron in (self.m, self.h, self.d, self.M, self.D)
        )
