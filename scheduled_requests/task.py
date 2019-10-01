request_params_allowed = {
    "url", "method", "params", "data",
    "json", "headers", "cookies", "files",
    "auth", "timeout"
}
task_params_allowed = { "schedule" }

from .utils import merge

class Task:
    ''' Compiled task object without any loader variables '''
    def __init__(self, name, task_params, request_params):
        self.name = name
        self.task_params = task_params
        self.request_params = request_params

    def __repr__(self):
        return "<Task %s> %s %s" % (self.name, repr(self.task_params), repr(self.request_params))

    def __str__(self):
        from yaml import dump
        return "* Task: %s\n> Parameters:\n%s\n%s\n" % (
            self.name, dump(self.task_params, indent=2), dump(self.request_params, indent=2))


    @classmethod
    def load_yaml(cls, path):
        ''' Load task template from yaml file and convert to task objects list '''
        import yaml
        with open(path, "r") as f:
            tasks = yaml.safe_load(f)
        return cls.load_task(tasks)

    @classmethod
    def load_task(cls, task, task_params_parent=None, request_params_parent=None):
        ''' Recursively compile task template (dict) to a list of task objects '''

        # Get core parameters
        name = task.get('name', '')
        skip = task.get('skip', False)
        tasks = task.get('tasks', [])

        # Merge additional parameters
        task_params = merge(task, task_params_parent, allowed_keys=task_params_allowed)
        request_params = merge(task, request_params_parent, allowed_keys=request_params_allowed)

        # Decide whether this is a valid task
        valid_request = 'url' in request_params and 'method' in request_params

        current_tasks = []
        # Add itself to the list
        if valid_request and not skip:
            current_tasks.append(Task(name, task_params, request_params))

        # Add all subtasks to the list
        for t in tasks:
            current_tasks.extend(cls.load_task(t, task_params, request_params))
        return current_tasks




