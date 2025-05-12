from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.database import Base

class TemplateType(enum.Enum):
    """Types of image templates."""
    FEATURE_SHOWCASE = "feature_showcase"
    CASE_STUDY = "case_study"
    INDUSTRY_TRIVIA = "industry_trivia"
    PRODUCT_UPDATE = "product_update"
    TESTIMONIAL = "testimonial"
    EVENT = "event"
    GENERAL = "general"

class Template(Base):
    """Model for image templates."""
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    template_type = Column(Enum(TemplateType), nullable=False)
    background_path = Column(String(1024), nullable=True)
    width = Column(Integer, nullable=False, default=1200)
    height = Column(Integer, nullable=False, default=630)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSON, nullable=True)  # Store font info, colors, positioning, etc.
    
    def __repr__(self):
        return f"<Template(id={self.id}, name='{self.name}', type={self.template_type})>" 