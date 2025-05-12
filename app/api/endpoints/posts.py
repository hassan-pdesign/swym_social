from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.database import get_db
from app.models.content import ContentItem, Post, Platform, ContentStatus
from app.agents.post_generator import PostGenerator
from app.templates.image_generator import ImageGenerator
from app.models.templates import TemplateType
from app.scheduler.post_scheduler import PostScheduler

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_posts(
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None,
    platform: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all posts with optional filtering."""
    query = db.query(Post)
    
    if status:
        try:
            content_status = ContentStatus(status)
            query = query.filter(Post.status == content_status)
        except ValueError:
            pass
    
    if platform:
        try:
            post_platform = Platform(platform)
            query = query.filter(Post.platform == post_platform)
        except ValueError:
            pass
    
    posts = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": post.id,
            "content_item_id": post.content_item_id,
            "text_content": post.text_content[:200] + "..." if len(post.text_content) > 200 else post.text_content,
            "image_path": post.image_path,
            "status": post.status.value,
            "platform": post.platform.value,
            "scheduled_time": post.scheduled_time.isoformat() if post.scheduled_time else None,
            "published_time": post.published_time.isoformat() if post.published_time else None,
            "created_at": post.created_at.isoformat(),
        }
        for post in posts
    ]

@router.post("/generate", response_model=dict)
async def generate_post(
    data: dict,
    db: Session = Depends(get_db)
):
    """Generate a new post from a content item."""
    content_item_id = data.get("content_item_id")
    platform_str = data.get("platform", "linkedin")
    
    if not content_item_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="content_item_id is required"
        )
    
    content_item = db.query(ContentItem).filter(ContentItem.id == content_item_id).first()
    
    if not content_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content item with ID {content_item_id} not found"
        )
    
    try:
        # Convert platform string to enum
        try:
            platform = Platform(platform_str.lower())
        except ValueError:
            platform = Platform.LINKEDIN  # Default to LinkedIn
        
        # Generate post
        generator = PostGenerator()
        post = generator.generate_post(content_item, platform)
        
        # Add to database
        db.add(post)
        db.commit()
        db.refresh(post)
        
        return {
            "id": post.id,
            "content_item_id": post.content_item_id,
            "text_content": post.text_content,
            "platform": post.platform.value,
            "status": post.status.value,
            "created_at": post.created_at.isoformat(),
            "message": f"Successfully generated post for {platform.value}"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating post: {str(e)}"
        )

@router.post("/{post_id}/generate-image", response_model=dict)
async def generate_post_image(
    post_id: int,
    template_type_str: Optional[str] = "general",
    db: Session = Depends(get_db)
):
    """Generate an image for a post."""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {post_id} not found"
        )
    
    try:
        # Convert template type string to enum
        try:
            template_type = TemplateType(template_type_str.lower())
        except ValueError:
            template_type = TemplateType.GENERAL
        
        # Generate image
        generator = ImageGenerator()
        image_path = generator.generate_image_for_post(post, template_type)
        
        if not image_path:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate image"
            )
        
        # Update post with image path
        post.image_path = image_path
        db.add(post)
        db.commit()
        
        return {
            "post_id": post.id,
            "image_path": post.image_path,
            "message": "Successfully generated image for post"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating image: {str(e)}"
        )

@router.post("/{post_id}/schedule", response_model=dict)
async def schedule_post(
    post_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Schedule a post for publication."""
    publish_time_str = data.get("publish_time")
    
    if not publish_time_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="publish_time is required"
        )
    
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {post_id} not found"
        )
    
    try:
        # Parse publish time
        publish_time = datetime.fromisoformat(publish_time_str.replace('Z', '+00:00'))
        
        # Schedule post
        scheduler = PostScheduler(db)
        success = scheduler.schedule_post(post, publish_time)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to schedule post"
            )
        
        return {
            "post_id": post.id,
            "platform": post.platform.value,
            "scheduled_time": post.scheduled_time.isoformat(),
            "message": f"Successfully scheduled post for {publish_time_str}"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid publish_time format: {str(e)}"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scheduling post: {str(e)}"
        )

@router.post("/{post_id}/publish", response_model=dict)
async def publish_post_now(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Publish a post immediately."""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {post_id} not found"
        )
    
    if post.status == ContentStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Post with ID {post_id} is already published"
        )
    
    try:
        # Set status to approved for immediate publishing
        post.status = ContentStatus.APPROVED
        db.add(post)
        db.commit()
        
        # Publish post
        scheduler = PostScheduler(db)
        success = scheduler.publish_post(post.id, post.platform)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to publish post"
            )
        
        # Refresh post to get updated data
        db.refresh(post)
        
        return {
            "post_id": post.id,
            "platform": post.platform.value,
            "published_time": post.published_time.isoformat() if post.published_time else None,
            "external_url": post.external_url,
            "message": "Successfully published post"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error publishing post: {str(e)}"
        )

@router.put("/{post_id}/status", response_model=dict)
async def update_post_status(
    post_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Update a post's status."""
    status_str = data.get("status")
    
    if not status_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="status is required"
        )
    
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {post_id} not found"
        )
    
    try:
        # Convert status string to enum
        try:
            new_status = ContentStatus(status_str.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_str}"
            )
        
        # Update post status
        post.status = new_status
        post.updated_at = datetime.utcnow()
        db.add(post)
        db.commit()
        
        return {
            "post_id": post.id,
            "status": post.status.value,
            "message": f"Successfully updated post status to {new_status.value}"
        }
        
    except Exception as e:
        if not isinstance(e, HTTPException):
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating post status: {str(e)}"
            )
        else:
            raise e 