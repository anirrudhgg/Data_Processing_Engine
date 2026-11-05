import json
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data_processing_engine import (  # noqa: E402
    CSVParser, JSONParser, XMLParser, DataValidator,
    TextReportGenerator, HTMLReportGenerator, JSONReportGenerator,
    DataProcessor, DataParser, ReportGenerator,
)


class TestParsers(unittest.TestCase):
    def test_csv_basic(self):
        self.assertEqual(CSVParser().parse("a,b\n1,2"), [["a", "b"], ["1", "2"]])

    def test_csv_quoted_comma(self):
        self.assertEqual(CSVParser().parse('Alice,"Berlin, Germany"'), [["Alice", "Berlin, Germany"]])

    def test_csv_skips_blank_lines(self):
        self.assertEqual(CSVParser().parse("a,b\n\n1,2\n"), [["a", "b"], ["1", "2"]])

    def test_json_arrays_and_objects(self):
        self.assertEqual(JSONParser().parse('[["a", 1]]'), [["a", 1]])
        self.assertEqual(JSONParser().parse('[{"name": "a", "age": 1}]'), [["a", 1]])

    def test_json_rejects_non_list(self):
        with self.assertRaises(ValueError):
            JSONParser().parse('{"name": "a"}')

    def test_xml_records(self):
        raw = ("<record><field>Alice</field><field>30</field></record>"
               "<record><field>Bob</field><field>25</field></record>")
        self.assertEqual(XMLParser().parse(raw), [["Alice", "30"], ["Bob", "25"]])

    def test_xml_with_root_and_empty_field(self):
        raw = "<data><record><field>Bob</field><field/></record></data>"
        self.assertEqual(XMLParser().parse(raw), [["Bob", ""]])


class TestValidator(unittest.TestCase):
    def test_removes_incomplete_records(self):
        records = [["Alice", "30"], ["Bob", ""], [], ["Carl", "  "], ["Dana", None], ["Eve", 0]]
        self.assertEqual(DataValidator().validate(records), [["Alice", "30"], ["Eve", 0]])


class TestReports(unittest.TestCase):
    def test_text(self):
        self.assertEqual(TextReportGenerator().generate([["a", "b"], ["1", "2"]]), "a, b\n1, 2")

    def test_html_escapes_input(self):
        report = HTMLReportGenerator().generate([["<script>alert(1)</script>"]])
        self.assertNotIn("<script>", report)
        self.assertIn("&lt;script&gt;", report)

    def test_json(self):
        self.assertEqual(json.loads(JSONReportGenerator().generate([["a", 1]])), [["a", 1]])


class TestProcessor(unittest.TestCase):
    def test_end_to_end_each_format(self):
        cases = [
            (CSVParser(), "Alice,30\nBob,\nCharlie,25"),
            (JSONParser(), '[["Alice", "30"], ["Bob", ""], ["Charlie", "25"]]'),
            (XMLParser(), "<record><field>Alice</field><field>30</field></record>"
                          "<record><field>Bob</field><field></field></record>"
                          "<record><field>Charlie</field><field>25</field></record>"),
        ]
        for parser, raw in cases:
            with self.subTest(parser=type(parser).__name__):
                report = DataProcessor(parser, DataValidator(), TextReportGenerator()).process_and_report(raw)
                self.assertEqual(report, "Alice, 30\nCharlie, 25")

    def test_dependencies_can_be_mocked(self):
        parser = Mock(spec=DataParser)
        parser.parse.return_value = [["x"]]
        reporter = Mock(spec=ReportGenerator)
        reporter.generate.return_value = "done"

        result = DataProcessor(parser, DataValidator(), reporter).process_and_report("raw input")

        parser.parse.assert_called_once_with("raw input")
        reporter.generate.assert_called_once_with([["x"]])
        self.assertEqual(result, "done")


if __name__ == "__main__":
    unittest.main()
