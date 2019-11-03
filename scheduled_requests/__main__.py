from .taskrunner import TaskRunner
from .task import Task
import argparse

parser = argparse.ArgumentParser(description="Run python requests, scheduled.")
parser.add_argument('-c', '--config', metavar="conf", nargs=1, default=['tasks.yaml'],
    help="specify tasks configuration file")
parser.add_argument('--cron', '--run', action='store_true', help="cron mode, run tasks and quit")
parser.add_argument('--debug', action='store_true', help="parse config file and print")
parser.add_argument('-v', '--verbose', action='count', help="Enable verbose logging")

args = parser.parse_args()

# Load tasks
tasks = Task.load_yaml(args.config[0])

# Print tasks and exit
if args.debug:
    for t in tasks:
        print("=" * 50)
        print(t)
    exit(0)


# Run tasks
runner = TaskRunner(tasks)
if args.cron:
    runner.run()
else:
    runner.poll()
