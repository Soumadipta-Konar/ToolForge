import logging
import asyncio
import aiohttp
import re
from bs4 import BeautifulSoup
import requests
from typing import List, Dict

logger = logging.getLogger(__name__)

async def fetch_tool_page(session: aiohttp.ClientSession, url: str, sem: asyncio.Semaphore) -> Dict:
    async with sem:
        try:
            async with session.get(url, timeout=15) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    name_tag = soup.find('h1')
                    name = name_tag.text.strip() if name_tag else "Unknown Tool"
                    
                    desc_tag = soup.find('meta', {'name': 'description'})
                    desc = desc_tag['content'].strip() if desc_tag else "AI Tool"
                    desc = desc.split('Dang.ai')[0].strip()
                    if desc.endswith(' featured on'):
                        desc = desc.replace(' featured on', '')
                    
                    website_link = url
                    for a in soup.find_all('a', href=True):
                        if 'dang.ai' not in a['href'] and a['href'].startswith('http'):
                            if 'View tool' in a.text or a.text.strip().lower() == 'view tool':
                                website_link = a['href']
                                break
                                
                    return {
                        "name": name,
                        "url": website_link,
                        "description": desc,
                        "source": "Dang.ai Directory"
                    }
        except Exception as e:
            logger.debug(f"Failed to fetch {url}: {str(e)}")
        return None

async def extract_concurrently(tool_urls: List[str]) -> List[Dict]:
    sem = asyncio.Semaphore(30)
    async with aiohttp.ClientSession(headers={'User-Agent': 'Mozilla/5.0'}) as session:
        tasks = [fetch_tool_page(session, url, sem) for url in tool_urls]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

def extract_dang_tools(target_count: int = 1000) -> List[Dict]:
    logger.info("Fetching Dang.ai Sitemap to discover real SaaS tools...")
    try:
        sitemap_xml = requests.get('https://dang.ai/sitemap.xml', headers={'User-Agent':'Mozilla/5.0'}).text
    except Exception as e:
        logger.error(f"Failed to fetch sitemap: {e}")
        return []
        
    urls = re.findall(r'<loc>(.*?)</loc>', sitemap_xml)
    tool_urls = [u for u in urls if '/tool/' in u or '/ai-tool/' in u]
    logger.info(f"Discovered {len(tool_urls)} total tool URLs in sitemap.")
    
    # Grab 2500 urls to safely guarantee we hit 1000 pristine outputs after timeouts and deduplication
    tool_urls_to_fetch = tool_urls[:3000]
    
    logger.info(f"Extracting {len(tool_urls_to_fetch)} tool pages concurrently. This will take ~30 seconds...")
    results = asyncio.run(extract_concurrently(tool_urls_to_fetch))
    
    logger.info(f"Successfully extracted {len(results)} pristine AI SaaS tools.")
    return results[:target_count]
