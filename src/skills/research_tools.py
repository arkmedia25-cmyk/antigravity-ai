import requests
from bs4 import BeautifulSoup
from googlesearch import search
from src.memory.memory_manager import MemoryManager
from src.core.logging import get_logger
import time
import hashlib
import xml.etree.ElementTree as ET

logger = get_logger("skills.research")

class ResearchTools:
    def __init__(self):
        self.memory = MemoryManager(namespace="research")

    def google_search(self, query: str, num_results: int = 5) -> list:
        """Performs a Google search. If blocked/empty, falls back to DuckDuckGo."""
        logger.info(f"Searching Google for: {query}")
        results = []
        try:
            search_results = search(query, num_results=num_results, advanced=True)
            for result in search_results:
                results.append({
                    "title": result.title,
                    "url": result.url,
                    "description": result.description
                })
                time.sleep(1)
        except Exception as e:
            logger.error(f"Google search error: {e}")
        
        if not results:
            logger.info("Google returned 0 results. Falling back to DuckDuckGo...")
            return self.duckduckgo_search(query, num_results)
            
        return results

    def duckduckgo_search(self, query: str, num_results: int = 5) -> list:
        """Simplified DuckDuckGo search via direct web scraping for high reliability."""
        logger.info(f"Searching DuckDuckGo for: {query}")
        results = []
        try:
            url = f"https://duckduckgo.com/html/?q={query}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for i, result in enumerate(soup.find_all('div', class_='result'), start=1):
                if i > num_results: break
                title_tag = result.find('a', class_='result__a')
                snippet_tag = result.find('a', class_='result__snippet')
                if title_tag:
                    results.append({
                        "title": title_tag.get_text(),
                        "url": title_tag['href'],
                        "description": snippet_tag.get_text() if snippet_tag else ""
                    })
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
        return results

    def pubmed_search(self, query: str, num_results: int = 3) -> list:
        """Searches PubMed (NCBI Entrez) for clinical trials and academic papers."""
        logger.info(f"Searching PubMed for: {query}")
        results = []
        try:
            search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmode=json&retmax={num_results}"
            resp = requests.get(search_url, timeout=10)
            data = resp.json()
            id_list = data.get("esearchresult", {}).get("idlist", [])
            
            if not id_list:
                return []

            summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={','.join(id_list)}&retmode=json"
            summ_resp = requests.get(summary_url, timeout=10)
            summ_data = summ_resp.json()
            
            for pmid in id_list:
                article = summ_data.get("result", {}).get(pmid, {})
                results.append({
                    "pmid": pmid,
                    "title": article.get("title"),
                    "pubdate": article.get("pubdate"),
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                })
        except Exception as e:
            logger.error(f"PubMed search error: {e}")
        return results

    def get_pubmed_abstract(self, pmid: str) -> str:
        """Fetches the full abstract of a PubMed article."""
        logger.info(f"Fetching PubMed abstract for PMID: {pmid}")
        try:
            fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=text&rettype=abstract"
            resp = requests.get(fetch_url, timeout=10)
            return resp.text
        except Exception as e:
            logger.error(f"PubMed fetch error: {e}")
            return f"Error: {e}"

    def get_page_content(self, url: str) -> str:
        """Scrapes and cleans text content from a URL."""
        logger.info(f"Scraping content from: {url}")
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove scripts, styles, and non-content elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # Extract text
            text = soup.get_text(separator='\n')
            
            # Clean whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limit length to avoid context window flooding
            return text[:4000]
            
        except Exception as e:
            logger.error(f"Scraping error for {url}: {e}")
            return f"Error: {str(e)}"

    def save_research(self, topic: str, content: str) -> bool:
        """Saves a research finding to memory after checking for duplicates."""
        try:
            # Generate a unique key based on topic and content hash
            content_hash = hashlib.md5(content.encode()).hexdigest()[:10]
            safe_topic = "".join([c if c.isalnum() else "_" for c in topic[:30]]).lower()
            key = f"{safe_topic}_{content_hash}"
            
            # Check if this content is already saved (basic duplicate check)
            if self.memory.load(key):
                logger.info(f"Research finding already exists for {topic}, skipping.")
                return False
            
            data = {
                "topic": topic,
                "content": content,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.memory.save(key, data)
            logger.info(f"Research saved: {key}")
            return True
        except Exception as e:
            logger.error(f"Save research error: {e}")
            return False

# Singleton instance
research_tools = ResearchTools()
