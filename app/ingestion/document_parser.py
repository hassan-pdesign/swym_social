import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from app.models.content import ContentSource, ContentItem, ContentType
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class DocumentParser:
    """Parser for internal documents (markdown, txt, etc.)."""
    
    def __init__(self, session: Session, base_dir: str = "data/documents"):
        """Initialize the document parser.
        
        Args:
            session: SQLAlchemy database session
            base_dir: Base directory for documents
        """
        self.session = session
        self.base_dir = base_dir
        
        # Create the base directory if it doesn't exist
        os.makedirs(self.base_dir, exist_ok=True)
    
    def parse_document(self, source: ContentSource, file_path: Optional[str] = None) -> List[ContentItem]:
        """Parse a document file.
        
        Args:
            source: ContentSource object with document info
            file_path: Optional override path to the document
            
        Returns:
            List of ContentItem objects
        """
        path = file_path or source.url
        if not path or not os.path.exists(path):
            logger.error(f"Document path does not exist: {path}")
            return []
        
        try:
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # For simplicity, treat the whole document as one content item
            # More sophisticated parsing could split it into sections
            
            # Extract title from filename or first line
            filename = os.path.basename(path)
            title = os.path.splitext(filename)[0]
            
            # If the first line looks like a title (e.g., # Title in markdown)
            lines = content.split('\n')
            if lines and (lines[0].startswith('# ') or lines[0].startswith('Title:')):
                title = lines[0].replace('# ', '').replace('Title:', '').strip()
            
            content_item = ContentItem(
                source_id=source.id,
                title=title,
                content=content,
                url=path,
                ingested_at=datetime.utcnow(),
                meta_data={"file_type": os.path.splitext(path)[1]}
            )
            
            # Update source last_ingested timestamp
            source.last_ingested = datetime.utcnow()
            self.session.add(source)
            
            return [content_item]
            
        except Exception as e:
            logger.error(f"Error parsing document {path}: {str(e)}")
            return []
    
    def discover_documents(self, directory: Optional[str] = None) -> List[str]:
        """Discover document files in a directory.
        
        Args:
            directory: Directory to scan, defaults to self.base_dir
            
        Returns:
            List of document file paths
        """
        scan_dir = directory or self.base_dir
        
        if not os.path.exists(scan_dir):
            logger.error(f"Directory does not exist: {scan_dir}")
            return []
        
        try:
            document_paths = []
            
            for root, _, files in os.walk(scan_dir):
                for file in files:
                    # Only include common document types
                    if file.endswith(('.md', '.txt', '.docx', '.pdf', '.json')):
                        document_paths.append(os.path.join(root, file))
            
            return document_paths
            
        except Exception as e:
            logger.error(f"Error discovering documents in {scan_dir}: {str(e)}")
            return []
            
    def create_source_from_document(self, file_path: str, name: Optional[str] = None) -> ContentSource:
        """Create a ContentSource from a document file.
        
        Args:
            file_path: Path to the document file
            name: Optional name for the source
            
        Returns:
            ContentSource object
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document does not exist: {file_path}")
        
        source_name = name or os.path.basename(file_path)
        
        source = ContentSource(
            name=source_name,
            url=file_path,
            content_type=ContentType.DOCUMENT,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            meta_data={"file_type": os.path.splitext(file_path)[1]}
        )
        
        return source 