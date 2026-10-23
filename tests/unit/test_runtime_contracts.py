"""Installed parser and API output checks for the implemented pure modules."""
import io
from pathlib import Path
import unittest
import yaml
from jsonschema import Draft202012Validator
from pypdf import PdfWriter
from vdt.evidence.formats import validate_file, ALLOWED_PAIRS
from vdt.evidence import InvalidFile
from test_risk_engine import MF, make_risk


class RuntimeContractTests(unittest.TestCase):
    def test_risk_outputs_conform_to_frozen_openapi(self):
        root = Path(__file__).resolve().parents[2]
        document = yaml.safe_load((root / 'docs/design/openapi-v0.1.yaml').read_text(encoding='utf-8'))
        schema = {'$ref': '#/components/schemas/RiskComputed', 'components': document['components']}
        validator = Draft202012Validator(schema)
        for case in MF['cases']:
            with self.subTest(case=case['id']):
                validator.validate(make_risk(case).to_dict())

    def test_installed_pdf_parser_accepts_complete_readable_document(self):
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        buffer = io.BytesIO()
        writer.write(buffer)
        self.assertEqual(validate_file(buffer, 'sample.pdf', 'application/pdf', ALLOWED_PAIRS, 4096), 'application/pdf')

    def test_installed_pdf_parser_rejects_encrypted_document(self):
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        writer.encrypt('synthetic-test-password')
        buffer = io.BytesIO()
        writer.write(buffer)
        with self.assertRaises(InvalidFile):
            validate_file(buffer, 'encrypted.pdf', 'application/pdf', ALLOWED_PAIRS, 4096)
