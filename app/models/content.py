from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.database import Base

class ContentType(enum.Enum):
    """Types of content sources."""
    WEBSITE = "website"
    DOCUMENT = "document"
    MANUAL = "manual"
    PRODUCT = "product"
    CASE_STUDY = "case_study"
    BLOG = "blog"

class ContentStatus(enum.Enum):
    """Status of a content piece."""
    DRAFT = "draft"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    REJECTED = "rejected"

class Platform(enum.Enum):
    """Social media platforms."""
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"

class ContentSource(Base):
    """Model for content source."""
    __tablename__ = "content_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(2048), nullable=True)
    content_type = Column(Enum(ContentType), nullable=False)
    last_ingested = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSON, nullable=True)
    
    # Relationships
    content_items = relationship("ContentItem", back_populates="source")
    
    def __repr__(self):
        return f"<ContentSource(id={self.id}, name='{self.name}', type={self.content_type})>"

class ContentItem(Base):
    """Model for individual content items extracted from sources."""
    __tablename__ = "content_items"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("content_sources.id"))
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    url = Column(String(2048), nullable=True)
    ingested_at = Column(DateTime, default=datetime.utcnow)
    meta_data = Column(JSON, nullable=True)
    
    # Relationships
    source = relationship("ContentSource", back_populates="content_items")
    posts = relationship("Post", back_populates="content_item")
    
    def __repr__(self):
        return f"<ContentItem(id={self.id}, title='{self.title[:30]}...', source_id={self.source_id})>"

class Post(Base):
    """Model for social media posts."""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    content_item_id = Column(Integer, ForeignKey("content_items.id"), nullable=True)
    text_content = Column(Text, nullable=False)
    image_path = Column(String(1024), nullable=True)
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT)
    platform = Column(Enum(Platform), nullable=False)
    scheduled_time = Column(DateTime, nullable=True)
    published_time = Column(DateTime, nullable=True)
    external_id = Column(String(255), nullable=True)  # ID returned by the platform API
    external_url = Column(String(2048), nullable=True)  # URL of the published post
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSON, nullable=True)
    
    # Relationships
    content_item = relationship("ContentItem", back_populates="posts")
    
    def __repr__(self):
        return f"<Post(id={self.id}, platform={self.platform}, status={self.status})>" 