
from types import ModuleType
from sys import modules
import inspect

class PluginError(Exception):
    """wrapper class for all plugin errors"""
    def __init__(self, message:Exception, plugin:ModuleType):
        self.plugin = plugin
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.plugin.__name__}: {self.message}"
