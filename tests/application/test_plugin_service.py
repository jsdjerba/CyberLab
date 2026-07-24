import pytest
from application.plugin_service import PluginService
from application.plugins.registry import PluginRegistry
from unittest.mock import MagicMock

def test_service_discovery_flow():
    mock_loader = MagicMock()
    registry = PluginRegistry()
    service = PluginService(mock_loader, registry)
    
    # Configuration du mock pour retourner un plugin
    mock_plugin = MagicMock()
    mock_plugin.id.value = "TEST_01"
    mock_loader.load_from_dir.return_value = mock_plugin
    
    service.discover_plugins(["TEST_01"])
    
    assert len(service.list_plugins()) == 1
    assert service.get_plugin("TEST_01") == mock_plugin