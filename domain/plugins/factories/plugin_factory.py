from domain.plugins.entities.plugin import Plugin
from domain.plugins.value_objects.plugin_id import PluginId
from domain.plugins.value_objects.plugin_version import PluginVersion

class PluginFactory:
    @staticmethod
    def create(manifest: dict) -> Plugin:
        return Plugin(
            id=PluginId(manifest["id"]),
            version=PluginVersion(manifest["version"]),
            metadata=manifest.get("metadata", {})
        )