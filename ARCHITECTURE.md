# Architecture Map: ToolForge Data Pipeline

## Data Flow Diagram
1. **Source Discovery (`src/extractors/`)**
   - **Primary:** `dang_ai.py` (High-concurrency async scraper targeting `sitemap.xml`)
   - **Secondary:** `github_awesome.py` (Fallback / padding source)
2. **Sanitization (`src/processors/cleaner.py`)**
   - Deduplication by URL
   - Domain blocking (e.g., github.com, coursera.org)
   - Keyword blocking (e.g., "tutorial", "course", "reading list")
3. **Enrichment (`src/processors/enricher.py`)**
   - Maps raw `{name, url, description}` to the strict 36-column schema using LLM intelligence.
4. **Storage (`src/utils/db.py`)**
   - SQLite Database (`ai_tools.db`)
   - Safe Upsert Logic (`ON CONFLICT(url) DO UPDATE`)
5. **Delivery (`src/pipelines/orchestrator.py`)**
   - Exports the final state to `ai_tools.csv` for downstream consumption.

## Security & Resilience
- **Rate Limit Protection:** Implemented `asyncio.Semaphore(30)` to protect against Cloudflare/WAF bans.
- **Schema Enforcement:** Strict `typing.Dict` validation before CSV generation.
