class PluginError(Exception): pass
class InvalidPluginId(PluginError): pass
class InvalidPluginVersion(PluginError): pass
class InvalidManifest(PluginError): pass
class PluginNotFound(PluginError): pass
class DuplicatePlugin(PluginError): pass