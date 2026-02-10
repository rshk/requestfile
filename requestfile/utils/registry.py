class Registry:
    def __init__(self):
        self.items = {}

    def set(self, name, value, override=False):
        if not override and name in self.items:
            raise ValueError(f"Item {name} already defined")
        self.items[name] = value

    def get(self, name):
        return self.items[name]

    def __getitem__(self, name):
        return self.items[name]

    def declare(self, name):
        def decorator(fn):
            self.set(name, fn)
            return fn

        return decorator
