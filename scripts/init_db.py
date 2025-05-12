#!/usr/bin/env python
"""
Initialize the database with test data.
Run this script after setting up the database.
"""

import os
import sys
import logging
from datetime import datetime, timedelta

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Base, engine
from app.models.content import ContentSource, ContentItem, ContentType, Post, Platform, ContentStatus
from app.models.templates import Template, TemplateType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database with tables and test data."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if we already have data
        existing_sources = db.query(ContentSource).count()
        if existing_sources > 0:
            logger.info("Database already contains data. Skipping initialization.")
            return
        
        logger.info("Adding test data...")
        
        # Add content sources
        sources = [
            ContentSource(
                name="Company Blog",
                url="https://example.com/blog",
                content_type=ContentType.BLOG,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            ContentSource(
                name="Product Documentation",
                url="https://example.com/docs",
                content_type=ContentType.DOCUMENT,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            ContentSource(
                name="Case Studies",
                url="https://example.com/case-studies",
                content_type=ContentType.CASE_STUDY,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        
        db.add_all(sources)
        db.commit()
        
        # Add content items
        content_items = [
            ContentItem(
                source_id=1,
                title="Introducing Our New AI Feature",
                content="""
                # Introducing Our New AI Feature
                
                We're excited to announce the release of our latest AI-powered feature. This groundbreaking addition 
                to our platform leverages machine learning algorithms to provide unprecedented insights and automation.
                
                ## Key Benefits
                
                * Saves up to 40% of manual processing time
                * Increases accuracy by 85%
                * Provides real-time analytics and feedback
                
                Early adopters have reported significant productivity gains and cost savings. 
                Try it today and transform your workflow!
                """,
                url="https://example.com/blog/new-ai-feature",
                ingested_at=datetime.utcnow(),
                meta_data={
                    "classification": {
                        "primary_category": "product",
                        "secondary_category": "technology",
                        "keywords": ["AI", "machine learning", "automation", "productivity", "analytics"],
                        "summary": "Announcement of a new AI feature that improves efficiency and accuracy.",
                        "confidence": 0.92
                    }
                }
            ),
            ContentItem(
                source_id=2,
                title="Implementation Guide",
                content="""
                # Implementation Guide
                
                This document provides a comprehensive guide to implementing our platform in your organization.
                
                ## Prerequisites
                
                Before you begin, ensure you have the following:
                
                * Admin access to your system
                * Technical requirements document
                * API credentials
                
                ## Step 1: Installation
                
                Begin by installing our software using the provided package...
                
                ## Step 2: Configuration
                
                Configure the system according to your organizational needs...
                
                ## Step 3: Integration
                
                Connect with your existing systems through our API...
                """,
                url="https://example.com/docs/implementation-guide",
                ingested_at=datetime.utcnow(),
                meta_data={
                    "classification": {
                        "primary_category": "educational",
                        "secondary_category": "product",
                        "keywords": ["implementation", "guide", "installation", "configuration", "integration"],
                        "summary": "A comprehensive guide for implementing the platform.",
                        "confidence": 0.89
                    }
                }
            ),
            ContentItem(
                source_id=3,
                title="Global Shipping Company Success Story",
                content="""
                # Global Shipping Company Success Story
                
                Learn how one of the world's largest shipping companies transformed their operations with our platform.
                
                ## Challenge
                
                The company was struggling with inefficient tracking systems, leading to delays and customer dissatisfaction.
                
                ## Solution
                
                By implementing our platform, they were able to:
                
                * Create a centralized tracking system
                * Automate notification processes
                * Optimize routing algorithms
                
                ## Results
                
                "Since adopting this solution, we've seen a 35% reduction in delivery times and a 28% increase in customer satisfaction scores," 
                says Maria Rodriguez, CTO of the company.
                
                The implementation also resulted in:
                
                * 42% cost reduction in operational expenses
                * 30% decrease in support tickets
                * ROI within 6 months
                """,
                url="https://example.com/case-studies/global-shipping",
                ingested_at=datetime.utcnow(),
                meta_data={
                    "classification": {
                        "primary_category": "case_study",
                        "secondary_category": "company",
                        "keywords": ["success story", "shipping", "logistics", "ROI", "customer satisfaction"],
                        "summary": "Case study about a global shipping company that improved operations with our platform.",
                        "confidence": 0.95
                    }
                }
            )
        ]
        
        db.add_all(content_items)
        db.commit()
        
        # Add posts
        posts = [
            Post(
                content_item_id=1,
                text_content="""Exciting announcement! 🚀 We've just launched our new AI-powered feature!

Our latest innovation leverages cutting-edge machine learning to help you:
✅ Save 40% of manual processing time
✅ Increase accuracy by 85%
✅ Get real-time analytics

Early adopters are already seeing amazing results. Ready to transform your workflow?

Learn more: https://example.com/blog/new-ai-feature

#AIInnovation #ProductivityTools #MachineLearning""",
                status=ContentStatus.DRAFT,
                platform=Platform.LINKEDIN,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            Post(
                content_item_id=1,
                text_content="""Just launched: Our new AI feature saves customers 40% processing time while boosting accuracy by 85%! See how it works: https://example.com/blog/new-ai-feature #AI #Innovation""",
                status=ContentStatus.DRAFT,
                platform=Platform.TWITTER,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            Post(
                content_item_id=3,
                text_content="""💼 SUCCESS STORY: Global Shipping Transformation

One of the world's largest shipping companies faced major challenges with their tracking systems, leading to delays and unhappy customers.

After implementing our platform, they achieved:
• 35% faster deliveries
• 28% higher customer satisfaction
• 42% reduction in operational costs
• ROI in just 6 months

"This solution has completely transformed our operations." - Maria Rodriguez, CTO

Want similar results for your business? Let's talk!

#SupplyChain #Logistics #DigitalTransformation #BusinessSuccess #ShippingIndustry""",
                status=ContentStatus.DRAFT,
                platform=Platform.LINKEDIN,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        
        db.add_all(posts)
        db.commit()
        
        # Add templates
        templates = [
            Template(
                name="Blue Feature Showcase",
                description="Blue-themed template for feature announcements",
                template_type=TemplateType.FEATURE_SHOWCASE,
                width=1200,
                height=630,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                meta_data={
                    "colors": {
                        "primary": "#2980b9",
                        "secondary": "#3498db",
                        "accent": "#e67e22",
                        "text": "#ffffff"
                    },
                    "fonts": {
                        "title": "OpenSans-Bold.ttf",
                        "body": "OpenSans-Regular.ttf"
                    }
                }
            ),
            Template(
                name="Green Testimonial",
                description="Green-themed template for quotes and testimonials",
                template_type=TemplateType.TESTIMONIAL,
                width=1200,
                height=630,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                meta_data={
                    "colors": {
                        "primary": "#27ae60",
                        "secondary": "#2ecc71",
                        "accent": "#f39c12",
                        "text": "#ffffff"
                    },
                    "fonts": {
                        "title": "OpenSans-Bold.ttf",
                        "body": "OpenSans-Regular.ttf"
                    }
                }
            )
        ]
        
        db.add_all(templates)
        db.commit()
        
        logger.info("Database initialized successfully with test data.")
    
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db() 