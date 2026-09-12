import requests
import re
import logging
from typing import List, Dict

# Configure centralized logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

GITHUB_REPOS = [
    'steven2358/awesome-generative-ai',
    'filipecalegario/awesome-generative-ai',
    'imartinez/awesome-ai-tools',
    'mahbubiftekhar/awesome-ai-tools'
]

def fetch_raw_markdown(repo: str) -> str:
    """Fetches raw README.md content from a given GitHub repository."""
    url = f"https://raw.githubusercontent.com/{repo}/main/README.md"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch {repo}: {e}")
        return ""

def extract_tools_from_markdown(markdown_text: str) -> List[Dict]:
    """
    Parses Markdown text to extract tool names, URLs, and descriptions.
    Matches standard Awesome List formats: 
    - [Name](url) - description
    * [Name](url): description
    """
    tools = []
    # Regex to match markdown links followed by text
    pattern = re.compile(r'^[-\*]\s+\[([^\]]+)\]\((https?://[^\)]+)\)[-:\s]+(.*)$', re.MULTILINE)
    
    matches = pattern.findall(markdown_text)
    for name, link, desc in matches:
        desc_clean = re.sub(r'<[^>]+>', '', desc).strip()
        tools.append({
            "name": name.strip(),
            "url": link.strip(),
            "description": desc_clean
        })
        
    return tools

def run_extraction() -> List[Dict]:
    """Orchestrates the extraction across all targeted repositories."""
    logger.info("Initializing GitHub Extraction Pipeline...")
    all_raw_tools = []
    
    for repo in GITHUB_REPOS:
        logger.info(f"Scraping raw markdown from: {repo}")
        markdown = fetch_raw_markdown(repo)
        if markdown:
            extracted = extract_tools_from_markdown(markdown)
            all_raw_tools.extend(extracted)
            logger.info(f" -> Extracted {len(extracted)} raw items from {repo}.")
            
    logger.info(f"Extraction complete. Total raw items found: {len(all_raw_tools)}")
    return all_raw_tools
