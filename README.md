# Data Processing Engine

A small Python pipeline that parses raw data (CSV, JSON or XML), removes incomplete records and produces a report (text, HTML or JSON). It is an exercise in object-oriented design: every step is an interface with interchangeable implementations, so a new format can be added without touching the existing code.

Requires Python 3.10+ and no extra packages.

```
python data_processing_engine.py          # demo
python -m unittest discover tests -v      # run the 13 tests
```

## Design

```
raw text ──> DataParser ──> RecordValidator ──> ReportGenerator ──> report
             CSVParser      DataValidator       TextReportGenerator
             JSONParser                         HTMLReportGenerator
             XMLParser                          JSONReportGenerator
```

- **Strategy pattern:** `DataParser`, `RecordValidator` and `ReportGenerator` are abstract base classes. Each concrete class is one interchangeable strategy.
- **Dependency injection:** `DataProcessor` receives its parser, validator and reporter in the constructor instead of creating them. It only decides the order of the steps.
- **Open/closed principle:** a new format, such as YAML, is a new subclass; the processor does not change.
- **Single responsibility:** parsers only structure data, the validator only filters, and reporters only format.

## Usage

```python
from data_processing_engine import DataProcessor, CSVParser, DataValidator, HTMLReportGenerator

raw_csv = 'Name,City\nAlice,"Berlin, Germany"\nBob,\nCharlie,Munich'

processor = DataProcessor(
    parser=CSVParser(),
    validator=DataValidator(),
    reporter=HTMLReportGenerator(),
)
print(processor.process_and_report(raw_csv))
```

Output (Bob is removed because his city is missing):

```html
<ul>
  <li>Name, City</li>
  <li>Alice, Berlin, Germany</li>
  <li>Charlie, Munich</li>
</ul>
```

## Input formats

| Parser | Expected input |
|---|---|
| `CSVParser` | Comma-separated lines; quoted fields may contain commas (uses Python's `csv` module) |
| `JSONParser` | An array of arrays, or an array of objects |
| `XMLParser` | `<record><field>…</field></record>` elements, with or without a root element (uses `xml.etree.ElementTree`) |

`HTMLReportGenerator` escapes every value, so input such as `<script>` is shown as text instead of running in a browser.

## Tests

`tests/test_data_processing_engine.py` checks each parser (including quoted commas and empty XML fields), the validator, HTML escaping, the full pipeline for all three formats, and that the processor works with mocked dependencies.

## Adding a format

```python
class YAMLParser(DataParser):
    def parse(self, raw_data: str) -> list:
        import yaml
        return yaml.safe_load(raw_data)

processor = DataProcessor(YAMLParser(), DataValidator(), TextReportGenerator())
```
