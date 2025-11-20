from dataclasses import dataclass
from typing import Any



@dataclass()
class PluginResult:
    """Standardised result class"""
    name: str
    data: dict[Any, Any]
