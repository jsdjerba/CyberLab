from dataclasses import dataclass
from domain.plugins.value_objects.plugin_id import PluginId
from domain.plugins.value_objects.plugin_version import PluginVersion

@dataclass(frozen=True)
class Plugin:
    id: PluginId
    version: PluginVersion
    metadata: dict

    def is_compatible(self, engine_version: str) -> bool:
        # Logique de compatibilité basée sur le manifest/moteur
        min_ver = self.metadata.get("engine", {}).get("min_version", "0.0.0")
        return engine_version >= min_ver