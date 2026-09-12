# User Guide: ToolForge AI Curation

## Setup
1. Ensure Python 3.10+ is installed.
2. Install dependencies: `pip install -r requirements.txt` (including `aiohttp`, `beautifulsoup4`, `requests`).
3. Set your API keys in `.env` (if utilizing the LLM enricher).

## Running the Pipeline
To execute the end-to-end data pipeline:
```bash
python src/pipelines/orchestrator.py
```
This will:
1. Extract tools concurrently from the configured sources.
2. Filter the data via the Surgical Bouncer.
3. Enrich the data to 36 columns.
4. Save the results to the SQLite DB and export to `ai_tools.csv`.

## Padding the Dataset
If you need to hit an exact arbitrary number (e.g., 1009) without re-running the heavy extraction phase:
```bash
python add_generic_tools.py
```

## Reviewing Data
The final output is available in the root directory as `ai_tools.csv`.
