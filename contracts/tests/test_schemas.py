import json
import unittest
from pathlib import Path

from jsonschema.validators import validator_for

SCHEMAS = sorted((Path(__file__).parent.parent / "schemas").glob("*.json"))


class ContractSchemaTests(unittest.TestCase):
    def test_schemas_exist(self) -> None:
        self.assertTrue(SCHEMAS)

    def test_each_schema_is_valid_against_its_declared_draft(self) -> None:
        for path in SCHEMAS:
            with self.subTest(schema=path.name):
                schema = json.loads(path.read_text(encoding="utf-8"))
                self.assertIn("$schema", schema, "schema must declare its draft")
                # default=None: an unknown draft fails instead of silently using the newest.
                validator = validator_for(schema, default=None)
                self.assertIsNotNone(validator, f"unknown draft {schema['$schema']}")
                validator.check_schema(schema)


if __name__ == "__main__":
    unittest.main()
