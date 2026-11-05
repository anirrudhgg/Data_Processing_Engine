"""A small data pipeline: parse -> validate -> report.

Each step is an interface (abstract base class) with interchangeable
implementations (Strategy pattern), and DataProcessor receives them through
its constructor (dependency injection), so a step can be swapped or mocked
without changing the processor.
"""
import csv
import html
import io
import json
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from typing import Any, List

Record = List[Any]


# ==========================================
# INTERFACES
# ==========================================

class DataParser(ABC):
    @abstractmethod
    def parse(self, raw_data: str) -> List[Record]:
        """Turns raw text into a list of records (each record is a list of fields)."""


class RecordValidator(ABC):
    @abstractmethod
    def validate(self, records: List[Record]) -> List[Record]:
        """Returns only the records that pass the rules."""


class ReportGenerator(ABC):
    @abstractmethod
    def generate(self, records: List[Record]) -> str:
        """Formats records as a report."""


# ==========================================
# PARSERS
# ==========================================

class CSVParser(DataParser):
    def parse(self, raw_data: str) -> List[Record]:
        # The csv module handles quoted fields such as "Berlin, Germany"
        reader = csv.reader(io.StringIO(raw_data))
        return [row for row in reader if row]


class JSONParser(DataParser):
    """Accepts a JSON array of arrays, or an array of objects (values are taken in key order)."""

    def parse(self, raw_data: str) -> List[Record]:
        data = json.loads(raw_data)
        if not isinstance(data, list):
            raise ValueError("JSON input must be an array of records.")
        records = []
        for entry in data:
            if isinstance(entry, list):
                records.append(entry)
            elif isinstance(entry, dict):
                records.append(list(entry.values()))
            else:
                raise ValueError(f"Unsupported JSON record: {entry!r}")
        return records


class XMLParser(DataParser):
    """Expects <record><field>...</field>...</record> elements, with or without a root element."""

    def parse(self, raw_data: str) -> List[Record]:
        root = ET.fromstring(f"<root>{raw_data}</root>")
        return [[(field.text or "").strip() for field in record.iter("field")]
                for record in root.iter("record")]


# ==========================================
# VALIDATION
# ==========================================

class DataValidator(RecordValidator):
    """Removes empty records and records with any missing field."""

    @staticmethod
    def _is_present(field: Any) -> bool:
        return field is not None and str(field).strip() != ""

    def validate(self, records: List[Record]) -> List[Record]:
        return [record for record in records
                if record and all(self._is_present(field) for field in record)]


# ==========================================
# REPORTS
# ==========================================

class TextReportGenerator(ReportGenerator):
    def generate(self, records: List[Record]) -> str:
        return "\n".join(", ".join(str(field) for field in record) for record in records)


class HTMLReportGenerator(ReportGenerator):
    def generate(self, records: List[Record]) -> str:
        # html.escape stops input like <script> from running in the browser
        items = "".join(
            f"  <li>{html.escape(', '.join(str(field) for field in record))}</li>\n"
            for record in records
        )
        return f"<ul>\n{items}</ul>"


class JSONReportGenerator(ReportGenerator):
    def generate(self, records: List[Record]) -> str:
        return json.dumps(records, indent=2)


# ==========================================
# PROCESSOR
# ==========================================

class DataProcessor:
    def __init__(self, parser: DataParser, validator: RecordValidator, reporter: ReportGenerator):
        self.parser = parser
        self.validator = validator
        self.reporter = reporter

    def process_and_report(self, raw_data: str) -> str:
        records = self.parser.parse(raw_data)
        valid_records = self.validator.validate(records)
        return self.reporter.generate(valid_records)


if __name__ == "__main__":
    raw_csv = 'Name,City\nAlice,"Berlin, Germany"\nBob,\nCharlie,Munich'
    processor = DataProcessor(CSVParser(), DataValidator(), HTMLReportGenerator())
    print(processor.process_and_report(raw_csv))
