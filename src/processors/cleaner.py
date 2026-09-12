import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# The definitive blacklist to guarantee zero research papers, academic journals, or news articles.
BANNED_DOMAINS = {
    'arxiv.org', 'nytimes.com', 'wsj.com', 'wired.com', 'notion.site', 
    'paperswithcode.com', 'wikipedia.org', 'sequoiacap.com', 'techcrunch.com',
    'bloomberg.com', 'forbes.com', 'theverge.com', 'news.ycombinator.com',
    'reddit.com', 'twitter.com', 'x.com', 'youtube.com', 'doi.org', 'nature.com', 'science.org',
    'github.com', 'github.io', 'colab.research.google.com', 'huggingface.co', 'docs.google.com'
}

# The Surgical Bouncer Keywords
# If ANY of these words appear in the tool's description or name, it is destroyed.
BANNED_KEYWORDS = [
    'course', 'tutorial', 'book', 'learn', 'study', 'guide', 'explainer', 
    'reading list', 'papers', 'researchers', 'notebook', 'colab', 'step by step',
    'syllabus', 'curriculum', 'lecture', 'cheat-sheet', 'cheatsheet', 'dataset'
]

def is_valid_tool(name: str, url: str, desc: str) -> bool:
    """
    Evaluates a URL and Description against the strict blacklists. 
    Returns True if permitted (a valid SaaS tool), False if it is educational trash.
    """
    url_lower = url.lower()
    desc_lower = desc.lower()
    name_lower = name.lower()
    
    # 1. Check Domain Bouncer
    for domain in BANNED_DOMAINS:
        if domain in url_lower:
            return False
            
    # 2. Check Keyword Bouncer (Educational Trash)
    full_text = f"{name_lower} {desc_lower}"
    for keyword in BANNED_KEYWORDS:
        # Pad with spaces to ensure exact word match to avoid accidental blocking
        # Example: 'book' shouldn't block 'booking'
        # Actually, simpler to just use regex word boundary or simple in
        import re
        if re.search(r'\b' + re.escape(keyword) + r'\b', full_text):
            return False
            
    return True

def sanitize_tools(raw_tools: List[Dict]) -> List[Dict]:
    """
    Acts as the Bouncer. 
    1. Deduplicates based on exact URL matching.
    2. Filters out banned domains (papers, news) and banned keywords (courses, tutorials).
    """
    logger.info(f"Beginning sanitization of {len(raw_tools)} raw items...")
    
    unique_tools = {}
    banned_count = 0
    
    for tool in raw_tools:
        url = tool['url']
        name = tool['name']
        desc = tool['description']
        
        # Deduplication
        if url in unique_tools:
            continue
            
        # Strict Filtering
        if is_valid_tool(name, url, desc):
            unique_tools[url] = tool
        else:
            banned_count += 1
            
    pure_tools = list(unique_tools.values())
    logger.info(f"Sanitization complete. Blocked {banned_count} trash/educational items. Valid Pure SaaS Tools: {len(pure_tools)}")
    return pure_tools
