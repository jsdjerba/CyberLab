from domain.plugins.entities.plugin import Plugin
from domain.plugins.exceptions import DuplicatePlugin, PluginNotFound

class PluginRegistry:
    def __init__(self):
        self._plugins = {}

    def register(self, plugin: Plugin):
        if plugin.id.value in self._plugins:
            raise DuplicatePlugin(f"Plugin {plugin.id.value} already registered")
        self._plugins[plugin.id.value] = plugin

    def get(self, plugin_id: str) -> Plugin:
        if plugin_id not in self._plugins:
            raise PluginNotFound(plugin_id)
        return self._plugins[plugin_id]

    def list_all(self):
        return list(self._plugins.values())