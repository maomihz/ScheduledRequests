#!/usr/bin/env python3
import json

from time import sleep
from datetime import datetime

from requests import request
from pycron import has_been, is_now

from html2text import html2text


request_params = {
    "url", "method", "params", "data", "json", "headers", "cookies", "files",
    "auth", "timeout",
#     "allow_redirects", "proxies", "verify", "stream", "cert"
}

# https://stackoverflow.com/questions/20656135/python-deep-merge-dictionary-data
def merge(source, destination=dict(), allowed_keys=set(), blocked_keys=set()):
    result = dict()
    keys = source.keys() | destination.keys()
    if allowed_keys: # Whitelist mode
        keys &= allowed_keys
    if blocked_keys: # Blacklist mode
        keys -= blocked_keys
    for key in keys:
        if key not in destination:
            result[key] = source[key]
        elif key not in source:
            result[key] = destination[key]
        elif isinstance(source[key], dict) and isinstance(destination[key], dict):
            result[key] = merge(source[key], destination[key])
        else: # Fallback, take the source
            result[key] = source[key]
    return result


# Run a group
class TaskRunner:
    def __init__(self, tasks, rate_limit=3):
        self.last_run = datetime.now()
        self.curr_run = datetime.now()

        self.rate_limit = rate_limit
        self.tasks = tasks # Task root
        self.done = False

    # Run a "task group"
    def run(self, taskgroup, params=dict(), task_names=list()):
        # Determine task names
        names = task_names + [taskgroup.get('name', '')]
        print("* Task: %s" % ' > '.join(names))

        # Merge new parameters, block keys that do not inheret
        params = merge(taskgroup, params, blocked_keys={"name", "tasks", "skip"})

        # Check whether to make an actual request
        do_request = 'url' in params and 'method' in params
        match_schedule = 'schedule' not in params or has_been(params['schedule'], self.last_run, self.curr_run)
        skip = taskgroup.get('skip', False)

        # Print reasons why skip the request
        if skip:
            print("- Skipped due to explict skip")
        elif not do_request:
            print("- Skipped due to no request")
        elif not match_schedule:
            print("- Skipped due to schedule")
        print("params", json.dumps(params, indent=2))

        # Do the actual request, if condition satisfy
        if do_request and match_schedule and not skip:
            print("*" * 50)
            print("Tasks started: ", self.curr_run)
            r = request(**merge(params, allowed_keys=request_params))
            print(r.url)
            print(r.status_code)
            # print('\n'.join(html2text(r.text).split('\n')[:50]))
            print("+" * 50)

            # Rate limit sleep
            sleep(self.rate_limit)

        # Run the subtasks
        for task in taskgroup.get('tasks', []):
            self.run(task, merge(params), names)



    def trigger(self):
        self.curr_run = datetime.now()
        print("Trigger at", self.curr_run)
        self.run(self.tasks)
        self.last_run = self.curr_run


    # Keep running the tasks
    def poll(self):
        while not self.done:
            runner.trigger()
            sleep(60)




    # Construct runner from a yaml file
    @classmethod
    def load_yaml(cls, path):
        import yaml
        with open("tasks.yaml", "r") as f:
            tasks = yaml.safe_load(f)
        runner = TaskRunner(tasks)
        return runner



if __name__ == '__main__':
    runner = TaskRunner.load_yaml("tasks.yaml")
    runner.poll()
