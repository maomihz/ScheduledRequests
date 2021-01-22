request_params_allowed = {
    "url", "method", "params", "data",
    "json", "headers", "cookies", "files",
    "auth", "timeout"
}

task_params_default = {
    "schedule": "* * * * *"
}

loader_params_default = {
    "tasks": [],
    "repeat": 1
}

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
        return cls.load_task_list(tasks, task_params_parent=task_params_default)

    @classmethod
    def load_task_list(cls, task_list, **kwargs):
        """Load a list of tasks, if the argument is a list.
        Otherwise, treat as a single task."""
        tasks = []
        if isinstance(task_list, list):
            for task in task_list:
                tasks.extend(cls.load_task(task, **kwargs))
        else:
            tasks.extend(cls.load_task(task_list, **kwargs))

        return tasks

    @classmethod
    def load_task(cls, task, task_params_parent=None, request_params_parent=None):
        ''' Recursively compile task template (dict) to a list of task objects '''

        # Merge additional parameters
        name = task.get('name', '')
        loader_params = merge(task, loader_params_default, allowed_keys=loader_params_default.keys())
        task_params = merge(task, task_params_parent, allowed_keys=task_params_default.keys())
        request_params = merge(task, request_params_parent, allowed_keys=request_params_allowed)
        tasks = []

        for i in range(loader_params['repeat']):
            # The request must be valid and is a leaf
            if cls.is_valid_request(request_params) and not loader_params['tasks']:
                tasks.append(Task(name, task_params, request_params))

            # Add all subtasks to the list
            tasks.extend(cls.load_task_list(
                loader_params['tasks'],
                task_params_parent=task_params,
                request_params_parent=request_params))

        return tasks

    @classmethod
    def is_valid_request(cls, request_params):
        """Check if a request is valid.

        A valid (complete) request requires at least url and method.
        """
        return 'url' in request_params and 'method' in request_params
