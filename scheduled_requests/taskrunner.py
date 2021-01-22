import logging

from time import sleep
from datetime import datetime

from requests import request
from pycron import is_now
import pytz

from html2text import html2text

logger = logging.getLogger(__name__)

class TaskRunner:
    def __init__(self, tasks, rate_limit=3):
        self.last_run_min = self._now_minutes()
        self.curr_run_min = self._now_minutes()

        self.rate_limit = rate_limit
        self.tasks = tasks  # Task root
        self.done = False

    def run(self, timenow=None):
        if timenow is None:
            timenow = datetime.now(pytz.utc)

        logger.info("Running tasks at %s", timenow)
        for task in self.tasks:
            logger.info("* Task: %s" % task.name)
            schedule = task.task_params['schedule']
            timenow_local = timenow.astimezone(task.task_params['timezone'])

            # Check schedule
            if not is_now(schedule, timenow_local):
                logger.info("- Skipped due to schedule")
                continue

            # Run the request
            logger.info("*" * 50)
            logger.info("Tasks started: %s", timenow)

            r = request(**task.request_params)
            logger.info(r.url)
            logger.info(r.status_code)

            logger.debug('\n'.join(html2text(r.text).split('\n')[:50]))
            logger.info("+" * 50)

            # Rate limit sleep
            sleep(self.rate_limit)


    def trigger(self):
        self.curr_run_min = self._now_minutes()
        if self.curr_run_min > self.last_run_min:
            self.run()
            self.last_run_min = self.curr_run_min
            return True
        logger.debug("Minute %s already done." % self.curr_run_min)
        return False


    # Keep running the tasks
    def poll(self):
        while not self.done:
            self.trigger()
            sleep(3)



    # Timestamp calculations
    def _now_minutes(self, dt=None):
        if dt is None:
            dt = datetime.now(pytz.utc)
        return self._timestamp_minutes(dt)

    def _timestamp_minutes(self, time):
        if hasattr(time, 'timestamp'):
            return self._timestamp_minutes(time.timestamp())
        return int(time / 60)
