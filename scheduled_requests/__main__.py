from .taskrunner import TaskRunner

runner = TaskRunner.load_yaml("tasks.yaml")
runner.poll()
