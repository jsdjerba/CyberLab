import json
from pathlib import Path
from domain.plugins.factories.plugin_factory import PluginFactory
from infrastructure.plugins.manifest_validator import ManifestValidator

class FileSystemLoader:
    def __init__(self, plugins_dir: str):
        self.plugins_dir = Path(plugins_dir).resolve()
        self.validator = ManifestValidator()

    def load_from_dir(self, plugin_dir_name: str):
        plugin_path = (self.plugins_dir / plugin_dir_name).resolve()
        
        # Sécurité : empêcher le Path Traversal
        if not str(plugin_path).startswith(str(self.plugins_dir)):
            raise ValueError("Security violation: Path Traversal attempt")

        manifest_file = plugin_path / "manifest.json"
        if not manifest_file.exists():
            return None

        with open(manifest_file, "r") as f:
            data = json.load(f)

        self.validator.validate(data)
        return PluginFactory.create(data)