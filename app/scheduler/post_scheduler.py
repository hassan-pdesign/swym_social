import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from app.models.content import Post, ContentStatus, Platform
from app.services.social_publisher import LinkedInPublisher, TwitterPublisher, InstagramPublisher
from app.config import settings

logger = logging.getLogger(__name__)

class PostScheduler:
    """Scheduler for social media posts."""
    
    def __init__(self, db_session: Session):
        """Initialize the post scheduler.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session
        
        # Initialize social media publishers
        self.publishers = {
            Platform.LINKEDIN: LinkedInPublisher(),
            Platform.TWITTER: TwitterPublisher(),
            Platform.INSTAGRAM: InstagramPublisher()
        }
        
        # Configure job stores and executors
        jobstores = {
            'default': SQLAlchemyJobStore(url=settings.DATABASE_URL)
        }
        
        executors = {
            'default': ThreadPoolExecutor(20)
        }
        
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        
        # Create scheduler
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )
    
    def start(self):
        """Start the scheduler."""
        try:
            self.scheduler.start()
            logger.info("Post scheduler started")
        except Exception as e:
            logger.error(f"Error starting scheduler: {str(e)}")
    
    def shutdown(self):
        """Shutdown the scheduler."""
        try:
            self.scheduler.shutdown()
            logger.info("Post scheduler shut down")
        except Exception as e:
            logger.error(f"Error shutting down scheduler: {str(e)}")
    
    def schedule_post(self, post: Post, publish_time: datetime) -> bool:
        """Schedule a post for publication.
        
        Args:
            post: Post to schedule
            publish_time: Time to publish the post
            
        Returns:
            True if scheduling was successful, False otherwise
        """
        try:
            # Update post status and scheduled time
            post.status = ContentStatus.SCHEDULED
            post.scheduled_time = publish_time
            self.db_session.add(post)
            self.db_session.commit()
            
            # Add job to scheduler
            job_id = f"post_{post.id}_{post.platform.value}"
            self.scheduler.add_job(
                func=self.publish_post,
                trigger='date',
                run_date=publish_time,
                id=job_id,
                replace_existing=True,
                args=[post.id, post.platform]
            )
            
            logger.info(f"Scheduled post {post.id} for {publish_time} on {post.platform.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling post {post.id}: {str(e)}")
            return False
    
    def reschedule_post(self, post: Post, new_publish_time: datetime) -> bool:
        """Reschedule a post for a new publication time.
        
        Args:
            post: Post to reschedule
            new_publish_time: New time to publish the post
            
        Returns:
            True if rescheduling was successful, False otherwise
        """
        try:
            # Update post scheduled time
            post.scheduled_time = new_publish_time
            self.db_session.add(post)
            self.db_session.commit()
            
            # Reschedule job
            job_id = f"post_{post.id}_{post.platform.value}"
            self.scheduler.reschedule_job(
                job_id=job_id,
                trigger='date',
                run_date=new_publish_time
            )
            
            logger.info(f"Rescheduled post {post.id} for {new_publish_time} on {post.platform.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error rescheduling post {post.id}: {str(e)}")
            return False
    
    def cancel_post(self, post: Post) -> bool:
        """Cancel a scheduled post.
        
        Args:
            post: Post to cancel
            
        Returns:
            True if cancellation was successful, False otherwise
        """
        try:
            # Update post status
            post.status = ContentStatus.DRAFT
            post.scheduled_time = None
            self.db_session.add(post)
            self.db_session.commit()
            
            # Remove job from scheduler
            job_id = f"post_{post.id}_{post.platform.value}"
            self.scheduler.remove_job(job_id)
            
            logger.info(f"Cancelled scheduled post {post.id} on {post.platform.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling post {post.id}: {str(e)}")
            return False
    
    def publish_post(self, post_id: int, platform: Platform) -> bool:
        """Publish a post to a social media platform.
        
        Args:
            post_id: ID of the post to publish
            platform: Platform to publish to
            
        Returns:
            True if publication was successful, False otherwise
        """
        try:
            # Create a new session for this thread
            session_factory = self.db_session.get_bind().engine.raw_connection
            session = Session(bind=session_factory())
            
            # Get post from database
            post = session.query(Post).filter(Post.id == post_id).first()
            
            if not post:
                logger.error(f"Post {post_id} not found")
                return False
            
            if post.status != ContentStatus.SCHEDULED and post.status != ContentStatus.APPROVED:
                logger.error(f"Post {post_id} is not scheduled or approved (current status: {post.status})")
                return False
            
            # Get the appropriate publisher for the platform
            publisher = self.publishers.get(platform)
            
            if not publisher:
                logger.error(f"No publisher available for platform {platform}")
                return False
            
            # Publish the post
            result = publisher.publish(post)
            
            if result.get("success"):
                # Update post status and metadata
                post.status = ContentStatus.PUBLISHED
                post.published_time = datetime.utcnow()
                post.external_id = result.get("post_id")
                post.external_url = result.get("post_url")
                
                if post.metadata:
                    metadata = post.metadata
                else:
                    metadata = {}
                
                metadata.update({
                    "publish_result": result
                })
                
                post.metadata = metadata
                session.add(post)
                session.commit()
                
                logger.info(f"Successfully published post {post_id} to {platform.value}")
                return True
            else:
                # Update post status to failed
                post.status = ContentStatus.FAILED
                
                if post.metadata:
                    metadata = post.metadata
                else:
                    metadata = {}
                
                metadata.update({
                    "publish_error": result.get("error"),
                    "publish_attempt": datetime.utcnow().isoformat()
                })
                
                post.metadata = metadata
                session.add(post)
                session.commit()
                
                logger.error(f"Failed to publish post {post_id} to {platform.value}: {result.get('error')}")
                return False
            
        except Exception as e:
            logger.error(f"Error publishing post {post_id} to {platform.value}: {str(e)}")
            return False
        finally:
            if 'session' in locals():
                session.close()
    
    def get_scheduled_posts(self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get scheduled posts within a time range.
        
        Args:
            start_time: Start time for range query, defaults to now
            end_time: End time for range query, defaults to 7 days from now
            
        Returns:
            List of scheduled post information
        """
        if start_time is None:
            start_time = datetime.utcnow()
        
        if end_time is None:
            end_time = start_time + timedelta(days=7)
        
        try:
            scheduled_posts = self.db_session.query(Post).filter(
                Post.status == ContentStatus.SCHEDULED,
                Post.scheduled_time >= start_time,
                Post.scheduled_time <= end_time
            ).all()
            
            result = []
            for post in scheduled_posts:
                result.append({
                    "post_id": post.id,
                    "platform": post.platform.value,
                    "scheduled_time": post.scheduled_time.isoformat() if post.scheduled_time else None,
                    "content_preview": post.text_content[:100] + "..." if len(post.text_content) > 100 else post.text_content
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting scheduled posts: {str(e)}")
            return [] 