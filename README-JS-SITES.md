# Handling JavaScript-Rendered Sites in Swym Social

This document explains how the web scraper handles JavaScript-rendered websites for content ingestion.

## Overview

Modern websites often use JavaScript to render content dynamically. The enhanced scraper in this application uses two approaches:

1. **Standard Requests + BeautifulSoup** (faster, works for static sites)
2. **Playwright Headless Browser** (slower but works for JS-rendered sites)

The system tries the faster method first, then falls back to the headless browser if no content is found.

## How It Works

The web scraping process follows these steps:

1. First attempts to scrape with standard HTTP requests and BeautifulSoup
2. If no content is found, it uses Playwright to render the page with JavaScript
3. Waits for selectors to appear on the page
4. Takes a screenshot for debugging purposes
5. Extracts content using various selectors and patterns
6. If all else fails, extracts text directly using JavaScript

## Usage

To handle JavaScript-rendered sites, make sure:

1. Playwright is installed:
   ```bash
   python -m playwright install
   ```

2. The necessary dependencies are in requirements.txt:
   ```
   playwright>=1.30.0
   beautifulsoup4>=4.10.0
   requests>=2.27.1
   ```

## Testing the Scraper

You can test the scraper directly using the included test script:

```bash
python scripts/test_scraper.py "https://your-javascript-site.com"
```

## Debugging

If scraping fails:

1. Check the logs for errors
2. Examine the screenshots in `data/screenshots/` directory
3. Try running the test script with the specific URL

## Common Issues and Solutions

1. **Page times out**: Increase the timeout in the Playwright configuration
2. **Content not found**: Add more CSS selectors to the scraper's patterns
3. **JavaScript execution fails**: Try different wait conditions or selectors

## Implementation Details

The implementation can be found in `app/ingestion/scraper.py`. Key components:

- `WebScraper` class handles both scraping methods
- `_scrape_with_requests` uses standard requests
- `_scrape_with_playwright` uses the headless browser
- `_parse_html_content` extracts content from HTML using various patterns 