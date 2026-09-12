import os
import sys
import csv
import logging

# Add src to the path for module resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.extractors.dang_ai import extract_dang_tools
from src.processors.cleaner import sanitize_tools
from src.processors.enricher import process_batch_enrichment
from src.utils.db import get_connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

TARGET_COUNT = 1000

def insert_to_db(enriched_tools: list):
    """Upserts the fully enriched tools into the SQLite Database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    upsert_count = 0
    for tool in enriched_tools:
        cursor.execute('''
            INSERT INTO ai_tools (url, name, description, status, category, primary_task, use_cases, pros, cons, total_score, enriched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                name=excluded.name,
                description=excluded.description,
                category=excluded.category,
                primary_task=excluded.primary_task,
                use_cases=excluded.use_cases,
                pros=excluded.pros,
                cons=excluded.cons,
                total_score=excluded.total_score,
                enriched_at=excluded.enriched_at
        ''', (
            tool['Official Website'], tool['Tool Name'], tool['Detailed Overview'], 'enriched',
            tool['Categories / Tags'], tool['Primary Task'], tool['Main Use Cases'],
            tool['Pros'], tool['Cons'], tool['Total Score (100)'], tool['Last Verified Date']
        ))
        upsert_count += 1
        
    conn.commit()
    conn.close()
    logger.info(f"Successfully upserted {upsert_count} records into SQLite database.")

def export_to_csv(enriched_tools: list):
    """Exports the exact 36 columns to ai_tools.csv."""
    if not enriched_tools:
        logger.error("No tools to export!")
        return
        
    target_path = os.path.join(os.path.dirname(__file__), '../../ai_tools.csv')
    keys = enriched_tools[0].keys()
    
    with open(target_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(enriched_tools)
        
    logger.info(f"SUCCESS: Exported {len(enriched_tools)} flawless records to {target_path}.")

def main():
    logger.info("Starting Enterprise Curation Pipeline DAG...")
    
    TARGET_COUNT = 1009
    
    # 1. Extract from Dang.ai (Primary)
    from src.extractors.github_awesome import run_extraction
    raw_tools = extract_dang_tools(target_count=2000)
    
    # Extract from GitHub (Secondary for Padding)
    github_tools = run_extraction()
    raw_tools.extend(github_tools)
    
    # 2. Clean (Bouncer)
    pure_tools = sanitize_tools(raw_tools)
    
    if len(pure_tools) < TARGET_COUNT:
        logger.warning(f"Extracted {len(pure_tools)} pure tools, which is short of the {TARGET_COUNT} target.")
    else:
        # Enforce exact target limit (1009)
        pure_tools = pure_tools[:TARGET_COUNT]
        
    # 3. Enrich
    logger.info("Passing pure tools into Intelligence Layer for procedural enrichment...")
    enriched_tools = process_batch_enrichment(pure_tools)
    
    # 4. Store
    insert_to_db(enriched_tools)
    
    # 5. Export
    export_to_csv(enriched_tools)
    logger.info("Pipeline DAG Execution Complete.")

if __name__ == '__main__':
    main()
