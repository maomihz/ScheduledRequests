from scheduled_requests import cron
from datetime import datetime
import unittest

now = datetime.now
CronTab = cron.CronTab

class TestCronTab(unittest.TestCase):
    def test_construct(self):
        cron.CronTab('4,*/3 */1 * * *')

    def test_replacement(self):
        t = cron.CronTab('* * * jan *')
        self.assertTrue(t.is_now(datetime(2019, 1, 1)))
        self.assertFalse(t.is_now(datetime(2019, 2, 2)))
        self.assertFalse(t.is_now(datetime(2019, 5, 2)))

    def test_replacement2(self):
        t = cron.CronTab('* * * * thu')
        self.assertTrue(t.is_now(datetime(2019, 1, 3)))
        self.assertTrue(t.is_now(datetime(2019, 1, 24)))
        self.assertFalse(t.is_now(datetime(2019, 2, 3)))
        self.assertFalse(t.is_now(datetime(2019, 2, 24)))

    def test_dow(self):
        t = cron.CronTab('* * * * 7')
        self.assertTrue(t.is_now(datetime(2019, 1, 6)))
        self.assertTrue(t.is_now(datetime(2019, 1, 27)))
        self.assertFalse(t.is_now(datetime(2019, 2, 6)))
        self.assertFalse(t.is_now(datetime(2019, 2, 27)))
        t = cron.CronTab('* * * * 0')
        self.assertTrue(t.is_now(datetime(2019, 1, 6)))
        self.assertTrue(t.is_now(datetime(2019, 1, 27)))
        self.assertFalse(t.is_now(datetime(2019, 2, 6)))
        self.assertFalse(t.is_now(datetime(2019, 2, 27)))

    def test_dow_range(self):
        t = cron.CronTab('* * * * 0-2')
        self.assertTrue(t.is_now(datetime(2019, 1, 6)))
        self.assertTrue(t.is_now(datetime(2019, 1, 7)))
        self.assertTrue(t.is_now(datetime(2019, 1, 8)))
        self.assertFalse(t.is_now(datetime(2019, 1, 9)))
        self.assertFalse(t.is_now(datetime(2019, 1, 10)))

        t = cron.CronTab('* * * * 5-7')
        self.assertTrue(t.is_now(datetime(2019, 1, 4)))
        self.assertTrue(t.is_now(datetime(2019, 1, 5)))
        self.assertTrue(t.is_now(datetime(2019, 1, 6)))
        self.assertFalse(t.is_now(datetime(2019, 1, 7)))
        self.assertFalse(t.is_now(datetime(2019, 1, 8)))

    def test_now(self):
        t = cron.CronTab('* * * * *')
        self.assertTrue(t.is_now())

    def test_every_minute(self):
        t = cron.CronTab('*/3 * * * *')
        self.assertTrue(t.is_now(now().replace(minute=0)))
        self.assertFalse(t.is_now(now().replace(minute=1)))
        self.assertFalse(t.is_now(now().replace(minute=2)))
        self.assertTrue(t.is_now(now().replace(minute=3)))

    def test_every_hour(self):
        t = cron.CronTab('7-22 */3 * * *')
        self.assertTrue(t.is_now(now().replace(minute=7, hour=0)))
        self.assertFalse(t.is_now(now().replace(minute=14, hour=1)))
        self.assertFalse(t.is_now(now().replace(minute=21, hour=2)))
        self.assertTrue(t.is_now(now().replace(minute=22, hour=3)))

    def test_every_day(self):
        t = cron.CronTab('7 */3 */4 * *')
        self.assertTrue(t.is_now(now().replace(minute=7, hour=6, day=1)))
        self.assertFalse(t.is_now(now().replace(minute=7, hour=6, day=2)))
        self.assertFalse(t.is_now(now().replace(minute=7, hour=6, day=3)))
        self.assertFalse(t.is_now(now().replace(minute=7, hour=6, day=4)))
        self.assertTrue(t.is_now(now().replace(minute=7, hour=6, day=5)))

    def test_every_range(self):
        t = cron.CronTab('15-20/2 * * * *')
        self.assertFalse(t.is_now(now().replace(minute=13)))
        self.assertFalse(t.is_now(now().replace(minute=14)))
        self.assertTrue(t.is_now(now().replace(minute=15)))
        self.assertFalse(t.is_now(now().replace(minute=16)))
        self.assertTrue(t.is_now(now().replace(minute=17)))
        self.assertFalse(t.is_now(now().replace(minute=20)))
        self.assertFalse(t.is_now(now().replace(minute=21)))


    def test_invalid_range(self):
        with self.assertRaises(ValueError):
            t = cron.CronTab('61 * * * *')
        with self.assertRaises(ValueError):
            t = cron.CronTab('0 5 * 34 *')

    def test_invalid_replacement(self):
        with self.assertRaises(ValueError):
            cron.CronTab('* * * jana *')
        with self.assertRaises(ValueError):
            cron.CronTab('* * * * sund')


