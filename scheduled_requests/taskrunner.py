import json

from time import sleep
from datetime import datetime

from requests import request
from pycron import is_now

from html2text import html2text

class TaskRunner:

    def __init__(self, tasks, rate_limit=3):
        self.last_run_min = self._now_minutes()
        self.curr_run_min = self._now_minutes()

        self.rate_limit = rate_limit
        self.tasks = tasks # Task root
        self.done = False

    def run(self, timenow=datetime.now()):
        print("Running tasks at", timenow)
        for task in self.tasks:
            print("* Task: %s" % task.name)
            schedule = task.task_params['schedule']

            # Check schedule
            if not is_now(schedule, timenow):
                print("- Skipped due to schedule")
                continue

            # Run the request
            print("*" * 50)
            print("Tasks started: ", timenow)
            r = request(**task.request_params)
            print(r.url)
            print(r.status_code)
            # print('\n'.join(html2text(r.text).split('\n')[:50]))
            print("+" * 50)

            # Rate limit sleep
            sleep(self.rate_limit)


    def trigger(self):
        self.curr_run_min = self._now_minutes()
        if self.curr_run_min > self.last_run_min:
            self.run()
            self.last_run_min += 1
            return True
        print("Minute %s already done." % self.curr_run_min)
        return False


    # Keep running the tasks
    def poll(self):
        while not self.done:
            self.trigger()
            sleep(3)



    # Timestamp calculations
    def _now_minutes(self, dt=datetime.now()):
        return self._timestamp_minutes(dt)

    def _timestamp_minutes(self, datetime):
        if hasattr(datetime, 'timestamp'):
            return int(datetime.timestamp() / 60)
        return int(datetime / 60)
