from .taskrunner import TaskRunner
from .task import Task

tasks = Task.load_yaml("tasks.yaml")
for t in tasks:
    print(t)

runner = TaskRunner(tasks)
runner.poll()
