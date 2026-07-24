import json
from pathlib import Path
from jsonschema import validate, ValidationError as SchemaError
from domain.plugins.exceptions import InvalidManifest

class ManifestValidator:
    def __init__(self):
        schema_path = Path(__file__).parent / "schema" / "plugin_manifest.schema.json"
        with open(schema_path, "r") as f:
            self.schema = json.load(f)

    def validate(self, manifest_data: dict):
        try:
            validate(instance=manifest_data, schema=self.schema)
        except SchemaError as e:
            raise InvalidManifest(f"Manifest validation failed: {e.message}")