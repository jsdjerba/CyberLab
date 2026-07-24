import json
import pytest
from infrastructure.plugins.filesystem_loader import FileSystemLoader

def test_path_traversal_prevention(tmp_path):
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    loader = FileSystemLoader(str(plugins_dir))
    
    # Tentative de sortir du dossier plugins
    with pytest.raises(ValueError, match="Security violation"):
        loader.load_from_dir("../secret")

def test_loader_loads_valid_plugin(tmp_path):
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    http_plugin = plugins_dir / "HTTP_01"
    http_plugin.mkdir()
    
    # Création d'un manifest valide
    manifest = {"id": "HTTP_01", "version": "1.0.0", "metadata": {"title": "Test", "category": "Web"}}
    (http_plugin / "manifest.json").write_text(json.dumps(manifest))
    
    loader = FileSystemLoader(str(plugins_dir))
    plugin = loader.load_from_dir("HTTP_01")
    assert plugin.id.value == "HTTP_01"