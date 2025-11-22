from types import ModuleType


class PluginError(Exception):
    """
    wrapper class for exceptions raised while running a plugin

    should not be used in a plugin, plugins should raise builtin/other custom exceptions
    which are caught and wrapped in a PluginError by the plugin runner

    self.plugin is a reference to the loaded plugin module - this lets us inform the user
    of which bit shit the bed without crashing the main app

    """

    def __init__(self, message: Exception, plugin: ModuleType):
        self.plugin = plugin
        print(self.plugin)
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.plugin.__name__}: {self.message}"
