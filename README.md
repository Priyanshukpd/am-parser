# AM Parser (Python)

Parse mutual fund Excel statements and extract portfolio into JSON using two approaches:
- Manual parsing (schema-based with header mapping)
- LLM parsing (provider-agnostic interface)

Inspired conceptually by `am-trade-management`, but implemented in Python for portfolio extraction.

## Features
- CLI with `parse-manual` and `parse-llm`
- Pluggable header maps for different statement formats
- Outputs normalized JSON schema
- Dry-run and output to file

## Project Structure

```
am-parser/
├── am_app/             # 🆕 Unified application interface (recommended entry point)
├── am_api/             # CLI interface module  
├── am_services/        # Core parsing services and data models
├── am_llm/             # LLM parsing functionality
├── am_persistence/     # Database repository interfaces  
├── am_common/          # Shared models and utilities
├── am_configs/         # Configuration files
├── am_parser/          # Backward compatibility wrapper (imports from external modules)
├── data/               # Sample data files
├── tests/              # Test files
└── docs/               # Documentation
```

**Design Philosophy:**
- **`am_app`** - High-level unified interface (CLI + programmatic API)
- **External modules** (`am_*`) contain the actual implementations
- **`am_parser`** package is a thin compatibility wrapper that imports from external modules  
- **Multiple entry points**: `python -m am_app` (recommended), `python -m am_api`, `python -m am_parser`
- **No code duplication** - each feature exists in exactly one place

## CLI Usage

**Unified Interface:** Use `am_app` for the most powerful command-line experience:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Analyze file structure first
python -m am_app analyze --input .\data\samples\mutualfund_sample.csv

# Parse with different methods
python -m am_app parse --input .\data\samples\mutualfund_sample.csv --method manual --show-preview
python -m am_app parse --input .\data\samples\mutualfund_sample.csv --method llm --dry-run
python -m am_app parse --input .\data\samples\mutualfund_sample.csv --method both --output comparison.json

# Batch processing
python -m am_app batch --input-dir .\data\samples\ --method manual --output-dir results\

# Save mutual fund portfolio JSON to MongoDB
python -m am_app save-portfolio --input .\data\mfextractedholdings\motilaloswalmf.json --dry-run
python -m am_app save-portfolio --input .\data\mfextractedholdings\motilaloswalmf.json --mongo-uri mongodb://localhost:27017
```

**Alternative interfaces:**
```powershell
# Basic CLI (single method)
python -m am_api parse-manual --input .\data\samples\mutualfund_sample.csv --out result.json

# Legacy wrapper (delegates to am_api)
python -m am_parser parse-manual --input .\data\samples\mutualfund_sample.csv --out result.json
```

## Programmatic Usage

### Portfolio Parsing
```python
# Simple single-file parsing
from am_app import parse_file

result = parse_file("portfolio.csv", method="manual", show_preview=True)
print(f"Found {len(result['holdings'])} holdings")

# Compare multiple methods
comparison = parse_file("portfolio.csv", method="both", output_file="comparison.json")
print("Comparison:", comparison['comparison'])

# Batch processing
from am_app import batch_parse

results = batch_parse(
    ["file1.csv", "file2.xlsx"], 
    method="manual",
    output_dir="results/"
)
```

### Mutual Fund Data Persistence
```python
# Load and persist mutual fund portfolio JSON to MongoDB
import json
import asyncio
from am_common import MutualFundPortfolio
from am_persistence import create_mutual_fund_service

async def save_portfolio():
    # Load JSON data
    with open("portfolio.json", 'r') as f:
        data = json.load(f)
    
    # Convert to model
    portfolio = MutualFundPortfolio(**data)
    
    # Save to MongoDB
    service = create_mutual_fund_service()
    portfolio_id = await service.save_portfolio(portfolio)
    print(f"Saved with ID: {portfolio_id}")
    
    # Retrieve and query
    retrieved = await service.get_portfolio(portfolio.mutual_fund_name, portfolio.portfolio_date)
    stats = await service.get_fund_statistics(portfolio.mutual_fund_name)
    await service.close()

asyncio.run(save_portfolio())
```

### Optional: MongoDB integration
- Install MongoDB support:
```powershell
pip install -r requirements-mongo.txt
```

- Start MongoDB locally or use cloud instance
- Use the mutual fund service:
```python
import asyncio
from am_common import MutualFundPortfolio
from am_persistence import create_mutual_fund_service

async def main():
    service = create_mutual_fund_service(
        mongo_uri="mongodb://localhost:27017", 
        db_name="mutual_funds"
    )
    
    # Load and save portfolio
    portfolio = MutualFundPortfolio(**json_data)
    portfolio_id = await service.save_portfolio(portfolio)
    
    # Query and retrieve
    stats = await service.get_fund_statistics(portfolio.mutual_fund_name)
    await service.close()

asyncio.run(main())
```
```powershell
# Set environment variables before running (optional)
$env:LLM_PROVIDER = "openai"
$env:OPENAI_API_KEY = "<your_key>"

# Parse with LLM
python -m am_api parse-llm --input .\data\samples\mutualfund_sample.csv --dry-run
python -m am_api parse-llm --input .\data\samples\mutualfund_sample.csv --out result.json
```
```

## JSON Output Schema
```json
{
  "fund": {
    "name": "...",
    "report_date": "YYYY-MM-DD",
    "currency": "INR" 
  },
  "holdings": [
    {"isin": "...", "ticker": "...", "name": "...", "sector": "...", "qty": 0, "mkt_value": 0.0, "weight": 0.0}
  ],
  "totals": {"mkt_value": 0.0, "weight": 100.0}
}
```

## Development
- Run tests: `pytest -q`
- Lint (optional): `ruff check .`
- Validate code conventions (size rules):
```powershell
python .\scripts\validate_code_conventions.py
```

### Optional: MongoDB integration
- Install extras:
```powershell
pip install -r requirements-mongo.txt
```
- Usage (example snippet):
```python
import asyncio
from am_common import Portfolio, Fund, Totals
from am_persistence import MongoPortfolioRepository

async def main():
    repo = MongoPortfolioRepository(uri="mongodb://localhost:27017", db_name="am_parser")
    portfolio = Portfolio(fund=Fund(), holdings=[], totals=Totals())
    doc_id = await repo.upsert(portfolio)
    loaded = await repo.get(doc_id)
    print(loaded)

asyncio.run(main())
```

## Notes
- The manual parser expects a tabular sheet with holdings. You can adjust header maps in `am_configs/header_maps.yaml`.
- The LLM parser will convert raw tables to normalized JSON using a prompt. It requires a supported provider and API key.
