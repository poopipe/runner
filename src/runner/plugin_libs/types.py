from dataclasses import dataclass
from typing import Any
from numpy import ndarray


@dataclass()
class PluginResult:
    """Standard result class"""

    name: str
    data: Any


@dataclass()
class PluginDictResult(PluginResult):
    """result class for dictionary data"""

    data: dict[Any, Any]


@dataclass()
class PluginMatResult(PluginResult):
    """result class for numpy ndarray data"""

    data: ndarray


@dataclass()
class PluginListResult(PluginResult):
    """result class for numpy ndarray data"""

    data: list[Any]
