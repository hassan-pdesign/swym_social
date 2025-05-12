from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.database import get_db
from app.models.content import ContentSource, ContentItem, ContentType
from app.ingestion.scraper import WebScraper
from app.ingestion.document_parser import DocumentParser
from app.agents.classifier import ContentClassifier

router = APIRouter()

@router.get("/sources", response_model=List[dict])
async def get_content_sources(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all content sources."""
    sources = db.query(ContentSource).offset(skip).limit(limit).all()
    return [
        {
            "id": source.id,
            "name": source.name,
            "url": source.url,
            "content_type": source.content_type.value,
            "is_active": source.is_active,
            "last_ingested": source.last_ingested.isoformat() if source.last_ingested else None,
            "created_at": source.created_at.isoformat(),
        }
        for source in sources
    ]

@router.post("/sources", response_model=dict)
async def create_content_source(
    source_data: dict,
    db: Session = Depends(get_db)
):
    """Create a new content source."""
    try:
        content_type = ContentType(source_data.get("content_type", "website"))
        
        source = ContentSource(
            name=source_data.get("name"),
            url=source_data.get("url"),
            content_type=content_type,
            is_active=source_data.get("is_active", True),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            meta_data=source_data.get("meta_data", {})
        )
        
        db.add(source)
        db.commit()
        db.refresh(source)
        
        return {
            "id": source.id,
            "name": source.name,
            "url": source.url,
            "content_type": source.content_type.value,
            "is_active": source.is_active,
            "created_at": source.created_at.isoformat(),
            "message": "Content source created successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating content source: {str(e)}"
        )

@router.post("/sources/{source_id}/ingest", response_model=dict)
async def ingest_content(
    source_id: int,
    db: Session = Depends(get_db)
):
    """Ingest content from a source."""
    source = db.query(ContentSource).filter(ContentSource.id == source_id).first()
    
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content source with ID {source_id} not found"
        )
    
    try:
        content_items = []
        
        if source.content_type == ContentType.WEBSITE:
            scraper = WebScraper(db)
            content_items = scraper.scrape_website(source)
            
        elif source.content_type == ContentType.DOCUMENT:
            parser = DocumentParser(db)
            content_items = parser.parse_document(source)
            
        else:
            # For other content types, you would implement specific ingesters
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ingestion for content type {source.content_type.value} not implemented"
            )
        
        # Save the content items
        for item in content_items:
            db.add(item)
        
        # Update the source last_ingested timestamp
        source.last_ingested = datetime.utcnow()
        db.add(source)
        
        db.commit()
        
        return {
            "source_id": source.id,
            "items_ingested": len(content_items),
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Successfully ingested {len(content_items)} items from {source.name}"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting content: {str(e)}"
        )

@router.get("/items", response_model=List[dict])
async def get_content_items(
    skip: int = 0, 
    limit: int = 100,
    source_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get content items with optional filtering by source."""
    query = db.query(ContentItem)
    
    if source_id:
        query = query.filter(ContentItem.source_id == source_id)
    
    items = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": item.id,
            "source_id": item.source_id,
            "title": item.title,
            "content": item.content[:200] + "..." if len(item.content) > 200 else item.content,  # Truncate long content
            "url": item.url,
            "ingested_at": item.ingested_at.isoformat(),
            "classification": item.meta_data.get("classification", {}) if item.meta_data else {},
        }
        for item in items
    ]

@router.post("/items/{item_id}/classify", response_model=dict)
async def classify_content_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """Classify a content item."""
    item = db.query(ContentItem).filter(ContentItem.id == item_id).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content item with ID {item_id} not found"
        )
    
    try:
        classifier = ContentClassifier()
        classification = classifier.classify_content(item)
        
        # Update the item's meta_data with classification
        if item.meta_data:
            meta_data = item.meta_data
        else:
            meta_data = {}
            
        meta_data["classification"] = {
            "primary_category": classification.get("primary_category"),
            "secondary_category": classification.get("secondary_category"),
            "keywords": classification.get("keywords", []),
            "summary": classification.get("summary"),
            "confidence": classification.get("confidence", 0.0)
        }
        
        item.meta_data = meta_data
        db.add(item)
        db.commit()
        
        return {
            "item_id": item.id,
            "classification": meta_data["classification"],
            "message": "Content classified successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error classifying content: {str(e)}"
        ) 