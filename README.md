# Extensible Data Processing Engine

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Design Pattern: Strategy](https://img.shields.io/badge/Pattern-Strategy-green.svg)](https://en.wikipedia.org/wiki/Strategy_pattern)
[![Architecture: SOLID](https://img.shields.io/badge/Architecture-SOLID-orange.svg)](https://en.wikipedia.org/wiki/SOLID)

A modular, enterprise-grade data processing pipeline built in Python. This system is designed to ingest raw data in various formats, validate the records against business rules, and generate formatted reports. 

The architecture strictly adheres to core **SOLID principles**, ensuring the codebase remains highly extensible, testable, and maintainable as new data sources and reporting requirements scale.

---

##  Architectural Patterns

The engine avoids tight coupling and monolithic procedural logic by leveraging behavioral design patterns and abstractions:

### 1. Strategy Pattern (Open/Closed Principle)
Data parsing and report generation are abstracted behind the `DataParser` and `ReportGenerator` Abstract Base Classes (ABCs).
- **Ingestion:** Supports dynamic swapping of `CSVParser`, `JSONParser`, and `XMLParser` without modifying the core execution logic. 
- **Extensibility:** New data formats (e.g., YAML) can be introduced simply by creating a new subclass, fully satisfying the Open/Closed Principle.

### 2. Dependency Injection (Dependency Inversion)
The core `DataProcessor` class does not instantiate its own dependencies. Instead, the specific parser, validator, and reporter are injected at runtime. 
- **Decoupling:** The processor acts purely as an orchestrator. It knows *when* to execute steps, but relies on injected dependencies to know *how* to execute them.
- **Testability:** This design allows for seamless unit testing by injecting mock parsers or reporters.

### 3. Single Responsibility Principle (SRP)
Data validation logic (e.g., stripping incomplete records) is entirely isolated into its own `DataValidator` service. Parsing classes are strictly responsible for structuring data, and reporters are strictly responsible for formatting, preventing domain overlap.

---

##  Usage & Implementation

The pipeline is assembled dynamically based on runtime requirements.

```python
from data_processing_engine import DataProcessor, CSVParser, DataValidator, HTMLReportGenerator

# 1. Define raw input
raw_csv = "Name,Age\nAlice,30\nBob,\nCharlie,25"

# 2. Assemble the pipeline via Dependency Injection
processor = DataProcessor(
    parser=CSVParser(),
    validator=DataValidator(),
    reporter=HTMLReportGenerator()
)

# 3. Execute processing (Automatically filters incomplete records like 'Bob')
report = processor.process_and_report(raw_csv)
print(report)
```

## Example Output:

```html
<ul>
  <li>['Name', 'Age']</li>
  <li>['Alice', '30']</li>
  <li>['Charlie', '25']</li>
</ul>
```

## Extensibility Guide:

To add support for a new output format (e.g., JSON Report), simply implement the `ReportGenerator` interface:

```python
class JSONReportGenerator(ReportGenerator):
    def generate(self, records: List[List[Any]]) -> str:
        import json
        return json.dumps(records, indent=2)
```

Pass `JSONReportGenerator()` into the `DataProcessor` upon instantiation, and the system will immediately adapt without core modifications.

