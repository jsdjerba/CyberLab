import pytest
from domain.plugins.entities.plugin import Plugin
from domain.plugins.value_objects.plugin_id import PluginId
from domain.plugins.value_objects.plugin_version import PluginVersion
from domain.plugins.exceptions import InvalidPluginId, InvalidPluginVersion

def test_plugin_creation_success():
    p = Plugin(PluginId("HTTP_01"), PluginVersion("1.0.0"), {"engine": {"min_version": "1.0"}})
    assert p.id.value == "HTTP_01"
    assert p.is_compatible("1.1") is True

def test_invalid_id():
    with pytest.raises(InvalidPluginId):
        PluginId("HTTP-01!") # Caractère interdit

def test_invalid_version():
    with pytest.raises(InvalidPluginVersion):
        PluginVersion("1.0") # Pas le bon format