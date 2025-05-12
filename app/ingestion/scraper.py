import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from app.models.content import ContentType, ContentSource, ContentItem
from sqlalchemy.orm import Session
import os

logger = logging.getLogger(__name__)

class WebScraper:
    """Web scraper for content ingestion."""
    
    def __init__(self, session: Session):
        """Initialize the scraper.
        
        Args:
            session: SQLAlchemy database session
        """
        self.session = session
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def scrape_website(self, source: ContentSource) -> List[ContentItem]:
        """Scrape content from a website.
        
        Args:
            source: ContentSource object with website info
            
        Returns:
            List of ContentItem objects
        """
        if not source.url:
            logger.error(f"No URL provided for source {source.id}")
            return []
        
        try:
            # First try with standard requests (faster for static sites)
            content_items = self._scrape_with_requests(source)
            
            # If no content items were found, try with Playwright (for JS-rendered sites)
            if not content_items:
                logger.info(f"No content found with standard scraper, trying with headless browser for: {source.url}")
                try:
                    content_items = asyncio.run(self._scrape_with_playwright(source))
                except Exception as e:
                    logger.error(f"Error scraping with Playwright: {str(e)}")
            
            # Update source last_ingested timestamp
            source.last_ingested = datetime.utcnow()
            self.session.add(source)
            
            return content_items
            
        except Exception as e:
            logger.error(f"Error scraping website {source.url}: {str(e)}")
            return []
    
    def _scrape_with_requests(self, source: ContentSource) -> List[ContentItem]:
        """Scrape content using requests and BeautifulSoup.
        
        Args:
            source: ContentSource object with website info
            
        Returns:
            List of ContentItem objects
        """
        try:
            response = requests.get(source.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            return self._parse_html_content(source, response.text)
            
        except Exception as e:
            logger.error(f"Error with requests scraper for {source.url}: {str(e)}")
            return []
    
    async def _scrape_with_playwright(self, source: ContentSource) -> List[ContentItem]:
        """Scrape content using Playwright for JavaScript-rendered sites.
        
        Args:
            source: ContentSource object with website info
            
        Returns:
            List of ContentItem objects
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=self.headers['User-Agent'],
                viewport={'width': 1280, 'height': 720}
            )
            
            page = await context.new_page()
            
            try:
                await page.goto(source.url, wait_until='networkidle', timeout=30000)
                
                # Wait for the page to load content - don't fail if selectors aren't found
                selectors = ['p', 'article', 'div.content', 'main', '.post-content', '.entry-content']
                
                # Try each selector but don't throw an exception if not found
                for selector in selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=2000, state='attached')
                        logger.info(f"Found selector {selector} on page")
                        break
                    except PlaywrightTimeoutError:
                        logger.debug(f"Selector {selector} not found on page")
                        continue
                
                # Wait a bit more for any JavaScript to finish executing
                await asyncio.sleep(2)
                
                # Get the HTML content
                html_content = await page.content()
                
                # Take a screenshot for debugging (optional)
                screenshot_path = f"data/screenshots/{source.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
                os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                await page.screenshot(path=screenshot_path, full_page=True)
                logger.info(f"Screenshot saved to {screenshot_path}")
                
                # Parse the HTML content
                content_items = self._parse_html_content(source, html_content)
                
                # If no content found with general selectors, try extracting all text as a fallback
                if not content_items:
                    logger.info("No content found with standard parsing, extracting all page text")
                    try:
                        # Extract all text from the page using JavaScript
                        all_text = await page.evaluate('''() => {
                            const elements = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, li, span');
                            return Array.from(elements)
                                .map(el => el.textContent.trim())
                                .filter(text => text.length > 20) // Only text with reasonable length
                                .join('\\n\\n');
                        }''')
                        
                        if all_text and len(all_text) > 100:  # Only if we got substantial text
                            # Get the page title
                            title = await page.title()
                            
                            # Create a content item with all text
                            content_item = ContentItem(
                                source_id=source.id,
                                title=title or f"Content from {source.url}",
                                content=all_text,
                                url=source.url,
                                ingested_at=datetime.utcnow(),
                                meta_data={
                                    "html_source": "javascript_extraction",
                                    "extraction_method": "fullpage_text",
                                    "screenshot_path": screenshot_path
                                }
                            )
                            content_items.append(content_item)
                    except Exception as js_error:
                        logger.error(f"Error extracting text with JavaScript: {str(js_error)}")
                
                return content_items
                
            except Exception as e:
                logger.error(f"Error with Playwright scraper for {source.url}: {str(e)}")
                return []
                
            finally:
                await browser.close()
    
    def _parse_html_content(self, source: ContentSource, html_content: str) -> List[ContentItem]:
        """Parse HTML content to extract content items.
        
        Args:
            source: ContentSource object with website info
            html_content: HTML content as string
            
        Returns:
            List of ContentItem objects
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        content_items = []
        
        # Try different content container patterns
        content_containers = []
        
        # 1. Check for articles
        articles = soup.find_all('article')
        if articles:
            content_containers.extend(articles)
        
        # 2. Check for main content
        main_content = soup.find('main')
        if main_content:
            content_containers.append(main_content)
            
        # 3. Check for common content classes
        for class_name in ['content', 'post-content', 'entry-content', 'article-content', 'blog-content', 'blog-post']:
            content_div = soup.find('div', class_=lambda c: c and class_name in c.split())
            if content_div:
                content_containers.append(content_div)
        
        # 4. If no content containers found, use body as fallback
        if not content_containers:
            body = soup.find('body')
            if body:
                content_containers.append(body)
        
        # Process each content container
        for container in content_containers:
            # Extract title
            title = None
            
            # Try to find title in different ways
            for title_selector in [
                # First try in the container
                lambda c: c.find(['h1', 'h2', 'h3']),
                # Then try in the full document
                lambda _: soup.find('h1'),
                lambda _: soup.find('h2'),
                lambda _: soup.find(['meta'], attrs={'property': 'og:title'})
            ]:
                title_elem = title_selector(container)
                if title_elem:
                    # Handle meta tags differently
                    if title_elem.name == 'meta':
                        title = title_elem.get('content', '').strip()
                    else:
                        title = title_elem.get_text().strip()
                    break
            
            # If still no title, try to get it from HTML title tag
            if not title:
                title_tag = soup.find('title')
                if title_tag:
                    title = title_tag.get_text().strip()
            
            # Extract content - gather all paragraphs
            paragraphs = container.find_all('p')
            content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            # If no paragraphs found, try other text containers (like list items)
            if not content:
                text_elements = container.find_all(['div', 'span', 'li'], text=True)
                filtered_texts = [el.get_text().strip() for el in text_elements 
                                  if el.get_text().strip() and len(el.get_text().strip()) > 30]
                if filtered_texts:
                    content = '\n\n'.join(filtered_texts)
            
            # If still no content but there's text content, use all text
            if not content and container.get_text().strip():
                # Clean up the text a bit
                content = '\n'.join(line.strip() for line in container.get_text().strip().split('\n') 
                                    if line.strip())
            
            if not content:
                continue
            
            # Create content item
            content_item = ContentItem(
                source_id=source.id,
                title=title or f"Content from {source.url}",
                content=content,
                url=source.url,
                ingested_at=datetime.utcnow(),
                meta_data={
                    "html_source": container.name,
                    "container_class": container.get('class', ''),
                    "container_id": container.get('id', '')
                }
            )
            
            content_items.append(content_item)
            
            # If we found content, no need to process other containers
            if content:
                break
        
        return content_items
    
    def extract_links(self, url: str) -> List[str]:
        """Extract links from a webpage.
        
        Args:
            url: URL to extract links from
            
        Returns:
            List of extracted URLs
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
            
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Make relative URLs absolute
                if not href.startswith(('http://', 'https://')):
                    href = urljoin(base_url, href)
                
                # Only include links from the same domain
                if urlparse(href).netloc == urlparse(url).netloc:
                    links.append(href)
            
            return list(set(links))  # Deduplicate
            
        except Exception as e:
            logger.error(f"Error extracting links from {url}: {str(e)}")
            return [] 