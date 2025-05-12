#!/usr/bin/env python3
"""
Test script to verify the enhanced scraper functionality
"""
import os
import sys
import json
from datetime import datetime
from sqlalchemy.orm import Session

# Add parent directory to path to allow importing app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import get_db, engine, Base
from app.models.content import ContentSource, ContentType
from app.ingestion.scraper import WebScraper

def test_scraper(url):
    """Test scraping a specific URL using both methods"""
    print(f"Testing scraper with URL: {url}")
    
    # Create engine and session
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    
    # Create a temporary content source
    source = ContentSource(
        name=f"Test Source {datetime.now().isoformat()}",
        url=url,
        content_type=ContentType.WEBSITE,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    try:
        # Add source to session but don't commit
        db.add(source)
        db.flush()
        
        # Create scraper
        scraper = WebScraper(db)
        
        print("\n1. Testing with regular requests:")
        # Test standard requests scraper
        items = scraper._scrape_with_requests(source)
        print(f"Found {len(items)} items with standard requests")
        if items:
            print_content_item(items[0])
        
        print("\n2. Testing with Playwright (headless browser):")
        # Test Playwright scraper
        import asyncio
        items = asyncio.run(scraper._scrape_with_playwright(source))
        print(f"Found {len(items)} items with Playwright")
        if items:
            print_content_item(items[0])
            
    finally:
        # Rollback to remove temporary source
        db.rollback()
        db.close()

def print_content_item(item):
    """Print a simplified view of a content item"""
    title = item.title or "No title"
    content_preview = item.content[:200] + "..." if len(item.content) > 200 else item.content
    meta_data = item.meta_data or {}
    
    print(f"Title: {title}")
    print(f"Content preview: {content_preview}")
    print(f"Metadata: {json.dumps(meta_data, indent=2)}")

if __name__ == "__main__":
    # Example JavaScript-rendered websites
    urls = [
        "https://www.getswym.com/blogs/what-your-shoppers-do-when-you-dont-have-a-wishlist-feature",
        "https://www.airbnb.com/",
        "https://www.nytimes.com/",
        "https://en.wikipedia.org/wiki/JavaScript"
    ]
    
    if len(sys.argv) > 1:
        # Use URL from command line if provided
        test_scraper(sys.argv[1])
    else:
        # Test the first URL by default
        test_scraper(urls[0]) 