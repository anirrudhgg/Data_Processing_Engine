from abc import ABC, abstractmethod
import json
from typing import List, Any

# ==========================================
# INTERFACES (ABSTRACTIONS)
# ==========================================

class DataParser(ABC):
    @abstractmethod
    def parse(self, raw_data: str) -> List[List[Any]]:
        pass

class ReportGenerator(ABC):
    @abstractmethod
    def generate(self, records: List[List[Any]]) -> str:
        pass


# ==========================================
# CONCRETE PARSERS (Strategy Pattern)
# ==========================================

class CSVParser(DataParser):
    def parse(self, raw_data: str) -> List[List[Any]]:
        lines = raw_data.split("\n")
        return [line.split(",") for line in lines if line]

class JSONParser(DataParser):
    def parse(self, raw_data: str) -> List[List[Any]]:
        return json.loads(raw_data)

class XMLParser(DataParser):
    def parse(self, raw_data: str) -> List[List[Any]]:
        records = []
        for chunk in raw_data.split("<record>"):
            if "</record>" in chunk:
                value = chunk.split("</record>")[0]
                records.append(value.split("<field>"))
        return records


# ==========================================
# VALIDATION (Single Responsibility Principle)
# ==========================================

class DataValidator:
    def validate(self, records: List[List[Any]]) -> List[List[Any]]:
        cleaned = []
        for record in records:
            if record:
                # all() returns True if all fields are non-empty
                if all(field != "" for field in record):
                    cleaned.append(record)
        return cleaned


# ==========================================
# CONCRETE REPORTERS (Strategy Pattern)
# ==========================================

class TextReportGenerator(ReportGenerator):
    def generate(self, records: List[List[Any]]) -> str:
        return "\n".join([str(record) for record in records])

class HTMLReportGenerator(ReportGenerator):
    def generate(self, records: List[List[Any]]) -> str:
        output = "<ul>\n"
        for record in records:
            output += f"  <li>{str(record)}</li>\n"
        output += "</ul>"
        return output


# ==========================================
# REFACTORED PROCESSOR (Dependency Injection)
# ==========================================

class DataProcessor:
    def __init__(self, parser: DataParser, validator: DataValidator, reporter: ReportGenerator):
        self.parser = parser
        self.validator = validator
        self.reporter = reporter

    def process_and_report(self, raw_data: str) -> str:
        # 1. Parse the raw data using the injected parser
        records = self.parser.parse(raw_data)
        
        # 2. Validate the records using the injected validator
        valid_records = self.validator.validate(records)
        
        # 3. Generate the report using the injected reporter
        return self.reporter.generate(valid_records)


# ==========================================
# USAGE EXAMPLE
# ==========================================
if __name__ == "__main__":
    raw_csv = "Name,Age\nAlice,30\nBob,\nCharlie,25"
    
    # We assemble the processor with exactly the components we need
    processor = DataProcessor(
        parser=CSVParser(),
        validator=DataValidator(),
        reporter=HTMLReportGenerator()
    )
    
    print("Generated HTML Report:")
    print(processor.process_and_report(raw_csv))