from .command import Command


class RequiredEnvVar:
    def __init__(self, name, env):
        self._name = name
        self._env = env

    @property
    def name(self):
        return f"MERKELY_{self._name}"

    def verify(self):
        self.value

    @property
    def value(self):
        result = self._env.get(self.name, None)
        if result is None:
            raise Command.Error(f"{self.name} environment-variable not set")
        if result == "":
            raise Command.Error(f"{self.name} environment-variable is empty string")
        return result
