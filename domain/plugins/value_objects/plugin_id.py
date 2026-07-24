import re
from dataclasses import dataclass
from domain.plugins.exceptions import InvalidPluginId

@dataclass(frozen=True)
class PluginId:
    value: str

    def __post_init__(self):
        if not re.match(r"^[a-zA-Z0-9_]+$", self.value):
            raise InvalidPluginId(f"Invalid Plugin ID: {self.value}")