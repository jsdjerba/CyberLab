from application.plugins.registry import PluginRegistry
from infrastructure.plugins.filesystem_loader import FileSystemLoader
from domain.plugins.exceptions import PluginError

class PluginService:
    def __init__(self, loader: FileSystemLoader, registry: PluginRegistry):
        self.loader = loader
        self.registry = registry

    def discover_plugins(self, plugin_names: list[str]):
        """Scanne le répertoire et enregistre les plugins valides."""
        for name in plugin_names:
            try:
                plugin = self.loader.load_from_dir(name)
                if plugin:
                    self.registry.register(plugin)
            except PluginError:
                # Log l'erreur mais continue pour ne pas bloquer tout le système
                continue

    def get_plugin(self, plugin_id: str):
        return self.registry.get(plugin_id)

    def list_plugins(self):
        return self.registry.list_all()