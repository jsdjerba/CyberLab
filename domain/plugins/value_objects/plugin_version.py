import re
from dataclasses import dataclass
from domain.plugins.exceptions import InvalidPluginVersion

@dataclass(frozen=True)
class PluginVersion:
    value: str

    def __post_init__(self):
        if not re.match(r"^\d+\.\d+\.\d+$", self.value):
            raise InvalidPluginVersion(f"Invalid version format: {self.value}")