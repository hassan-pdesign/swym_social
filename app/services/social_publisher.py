import os
import logging
import json
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod
from app.models.content import Post, Platform
from app.config import settings

logger = logging.getLogger(__name__)

class SocialPublisher(ABC):
    """Abstract base class for social media publishers."""
    
    @abstractmethod
    def publish(self, post: Post) -> Dict[str, Any]:
        """Publish a post to a social media platform.
        
        Args:
            post: Post to publish
            
        Returns:
            Dictionary with result information
        """
        pass
    
    @abstractmethod
    def delete(self, post_id: str) -> Dict[str, Any]:
        """Delete a post from a social media platform.
        
        Args:
            post_id: ID of the post to delete
            
        Returns:
            Dictionary with result information
        """
        pass
    
    @abstractmethod
    def get_post_stats(self, post_id: str) -> Dict[str, Any]:
        """Get statistics for a post on a social media platform.
        
        Args:
            post_id: ID of the post to get stats for
            
        Returns:
            Dictionary with statistics information
        """
        pass


class LinkedInPublisher(SocialPublisher):
    """Publisher for LinkedIn posts."""
    
    def __init__(self, access_token: Optional[str] = None):
        """Initialize the LinkedIn publisher.
        
        Args:
            access_token: LinkedIn API access token, defaults to settings
        """
        self.access_token = access_token or settings.LINKEDIN_ACCESS_TOKEN
        self.api_url = "https://api.linkedin.com/v2"
        
        # Person/Organization URN (would be set from settings in a real app)
        # Format: urn:li:person:{id} or urn:li:organization:{id}
        self.author_urn = "urn:li:person:me"
    
    def publish(self, post: Post) -> Dict[str, Any]:
        """Publish a post to LinkedIn.
        
        Args:
            post: Post to publish
            
        Returns:
            Dictionary with result information
        """
        if not self.access_token:
            return {"success": False, "error": "LinkedIn access token not configured"}
        
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            # Define the post content
            post_data = {
                "author": self.author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": post.text_content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            # Add image if available
            if post.image_path and os.path.exists(post.image_path):
                # In a real implementation, this would handle image upload to LinkedIn
                # For MVP, we'll just note that an image was included
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
                # The actual upload would involve multiple API calls to LinkedIn's media API
            
            # Make the API call to create the post
            response = requests.post(
                f"{self.api_url}/ugcPosts",
                headers=headers,
                json=post_data
            )
            
            if response.status_code == 201:
                post_id = response.headers.get('x-restli-id')
                return {
                    "success": True,
                    "post_id": post_id,
                    "post_url": f"https://www.linkedin.com/feed/update/{post_id}",
                    "platform": "linkedin",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"LinkedIn API error: {response.status_code} - {response.text}",
                    "platform": "linkedin",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error publishing to LinkedIn: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "platform": "linkedin",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def delete(self, post_id: str) -> Dict[str, Any]:
        """Delete a post from LinkedIn.
        
        Args:
            post_id: ID of the post to delete
            
        Returns:
            Dictionary with result information
        """
        if not self.access_token:
            return {"success": False, "error": "LinkedIn access token not configured"}
        
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            # Make the API call to delete the post
            response = requests.delete(
                f"{self.api_url}/ugcPosts/{post_id}",
                headers=headers
            )
            
            if response.status_code == 204:
                return {
                    "success": True,
                    "platform": "linkedin",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"LinkedIn API error: {response.status_code} - {response.text}",
                    "platform": "linkedin",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error deleting LinkedIn post: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "platform": "linkedin",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_post_stats(self, post_id: str) -> Dict[str, Any]:
        """Get statistics for a LinkedIn post.
        
        Args:
            post_id: ID of the post to get stats for
            
        Returns:
            Dictionary with statistics information
        """
        if not self.access_token:
            return {"success": False, "error": "LinkedIn access token not configured"}
        
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            # Make the API call to get post statistics
            # Note: LinkedIn's API for stats is more complex and may require multiple calls
            # This is a simplified implementation
            response = requests.get(
                f"{self.api_url}/socialActions/{post_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "stats": {
                        "likes": data.get("likesSummary", {}).get("totalLikes", 0),
                        "comments": data.get("commentsSummary", {}).get("totalComments", 0),
                        "shares": data.get("sharesSummary", {}).get("totalShares", 0)
                    },
                    "platform": "linkedin",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"LinkedIn API error: {response.status_code} - {response.text}",
                    "platform": "linkedin",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting LinkedIn post stats: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "platform": "linkedin",
                "timestamp": datetime.utcnow().isoformat()
            }


class TwitterPublisher(SocialPublisher):
    """Publisher for Twitter posts."""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None,
                 access_token: Optional[str] = None, access_secret: Optional[str] = None):
        """Initialize the Twitter publisher.
        
        Args:
            api_key: Twitter API key, defaults to settings
            api_secret: Twitter API secret, defaults to settings
            access_token: Twitter access token, defaults to settings
            access_secret: Twitter access token secret, defaults to settings
        """
        self.api_key = api_key or settings.TWITTER_API_KEY
        self.api_secret = api_secret or settings.TWITTER_API_SECRET
        self.access_token = access_token or settings.TWITTER_ACCESS_TOKEN
        self.access_secret = access_secret or settings.TWITTER_ACCESS_SECRET
        self.api_url = "https://api.twitter.com/2"
    
    def _get_bearer_token(self) -> Optional[str]:
        """Get a bearer token for Twitter API v2.
        
        Returns:
            Bearer token or None if authentication failed
        """
        try:
            auth_url = "https://api.twitter.com/oauth2/token"
            
            auth = (self.api_key, self.api_secret)
            data = {'grant_type': 'client_credentials'}
            
            response = requests.post(auth_url, auth=auth, data=data)
            
            if response.status_code == 200:
                return response.json().get('access_token')
            else:
                logger.error(f"Twitter authentication error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting Twitter bearer token: {str(e)}")
            return None
    
    def publish(self, post: Post) -> Dict[str, Any]:
        """Publish a post to Twitter.
        
        Args:
            post: Post to publish
            
        Returns:
            Dictionary with result information
        """
        if not all([self.api_key, self.api_secret, self.access_token, self.access_secret]):
            return {"success": False, "error": "Twitter API credentials not configured"}
        
        try:
            # For an actual implementation, we would use the Twitter API library
            # and handle OAuth 1.0a authentication properly
            # This is a simplified example using requests
            
            bearer_token = self._get_bearer_token()
            
            if not bearer_token:
                return {"success": False, "error": "Failed to authenticate with Twitter"}
            
            headers = {
                "Authorization": f"Bearer {bearer_token}",
                "Content-Type": "application/json"
            }
            
            # Twitter has a character limit, so truncate if necessary
            tweet_text = post.text_content
            if len(tweet_text) > 280:
                tweet_text = tweet_text[:277] + "..."
            
            post_data = {
                "text": tweet_text
            }
            
            # Add image if available (simplified)
            if post.image_path and os.path.exists(post.image_path):
                # In a real implementation, this would handle image upload to Twitter
                # For MVP, we'll just note that an image was included
                post_data["media"] = {"media_ids": ["placeholder_media_id"]}
            
            # Make the API call to create the tweet
            response = requests.post(
                f"{self.api_url}/tweets",
                headers=headers,
                json=post_data
            )
            
            if response.status_code == 201:
                data = response.json()
                tweet_id = data.get("data", {}).get("id")
                return {
                    "success": True,
                    "post_id": tweet_id,
                    "post_url": f"https://twitter.com/user/status/{tweet_id}",
                    "platform": "twitter",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Twitter API error: {response.status_code} - {response.text}",
                    "platform": "twitter",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error publishing to Twitter: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "platform": "twitter",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def delete(self, post_id: str) -> Dict[str, Any]:
        """Delete a post from Twitter.
        
        Args:
            post_id: ID of the post to delete
            
        Returns:
            Dictionary with result information
        """
        if not all([self.api_key, self.api_secret, self.access_token, self.access_secret]):
            return {"success": False, "error": "Twitter API credentials not configured"}
        
        try:
            bearer_token = self._get_bearer_token()
            
            if not bearer_token:
                return {"success": False, "error": "Failed to authenticate with Twitter"}
            
            headers = {
                "Authorization": f"Bearer {bearer_token}",
                "Content-Type": "application/json"
            }
            
            # Make the API call to delete the tweet
            response = requests.delete(
                f"{self.api_url}/tweets/{post_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "platform": "twitter",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Twitter API error: {response.status_code} - {response.text}",
                    "platform": "twitter",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error deleting Twitter post: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "platform": "twitter",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_post_stats(self, post_id: str) -> Dict[str, Any]:
        """Get statistics for a Twitter post.
        
        Args:
            post_id: ID of the post to get stats for
            
        Returns:
            Dictionary with statistics information
        """
        if not all([self.api_key, self.api_secret, self.access_token, self.access_secret]):
            return {"success": False, "error": "Twitter API credentials not configured"}
        
        try:
            bearer_token = self._get_bearer_token()
            
            if not bearer_token:
                return {"success": False, "error": "Failed to authenticate with Twitter"}
            
            headers = {
                "Authorization": f"Bearer {bearer_token}",
                "Content-Type": "application/json"
            }
            
            # Make the API call to get tweet metrics
            response = requests.get(
                f"{self.api_url}/tweets/{post_id}?tweet.fields=public_metrics",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                metrics = data.get("data", {}).get("public_metrics", {})
                
                return {
                    "success": True,
                    "stats": {
                        "likes": metrics.get("like_count", 0),
                        "retweets": metrics.get("retweet_count", 0),
                        "replies": metrics.get("reply_count", 0),
                        "impressions": metrics.get("impression_count", 0)
                    },
                    "platform": "twitter",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Twitter API error: {response.status_code} - {response.text}",
                    "platform": "twitter",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting Twitter post stats: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "platform": "twitter",
                "timestamp": datetime.utcnow().isoformat()
            }


class InstagramPublisher(SocialPublisher):
    """Publisher for Instagram posts."""
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None,
                 access_token: Optional[str] = None):
        """Initialize the Instagram publisher.
        
        Args:
            client_id: Instagram API client ID, defaults to settings
            client_secret: Instagram API client secret, defaults to settings
            access_token: Instagram access token, defaults to settings
        """
        self.client_id = client_id or settings.INSTAGRAM_CLIENT_ID
        self.client_secret = client_secret or settings.INSTAGRAM_CLIENT_SECRET
        self.access_token = access_token or settings.INSTAGRAM_ACCESS_TOKEN
        self.api_url = "https://graph.facebook.com/v18.0"  # Instagram Graph API is part of Facebook Graph API
    
    def publish(self, post: Post) -> Dict[str, Any]:
        """Publish a post to Instagram.
        
        Args:
            post: Post to publish
            
        Returns:
            Dictionary with result information
        """
        if not all([self.client_id, self.client_secret, self.access_token]):
            return {"success": False, "error": "Instagram API credentials not configured"}
        
        try:
            # Instagram requires an image for posts
            if not post.image_path or not os.path.exists(post.image_path):
                return {"success": False, "error": "Instagram posts require an image"}
            
            # For a real implementation, we would handle the Instagram Graph API properly
            # This is a simplified example
            
            # Step 1: Upload photo to obtain a container ID
            # In a real implementation, we would upload the image file
            container_id = "placeholder_container_id"
            
            # Step 2: Publish the container with caption
            params = {
                "access_token": self.access_token,
                "caption": post.text_content,
                "container_id": container_id
            }
            
            response = requests.post(
                f"{self.api_url}/me/media_publish",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                post_id = data.get("id")
                return {
                    "success": True,
                    "post_id": post_id,
                    "post_url": f"https://www.instagram.com/p/{post_id}",
                    "platform": "instagram",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Instagram API error: {response.status_code} - {response.text}",
                    "platform": "instagram",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error publishing to Instagram: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "platform": "instagram",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def delete(self, post_id: str) -> Dict[str, Any]:
        """Delete a post from Instagram.
        
        Args:
            post_id: ID of the post to delete
            
        Returns:
            Dictionary with result information
        """
        if not all([self.client_id, self.client_secret, self.access_token]):
            return {"success": False, "error": "Instagram API credentials not configured"}
        
        try:
            params = {
                "access_token": self.access_token
            }
            
            response = requests.delete(
                f"{self.api_url}/{post_id}",
                params=params
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "platform": "instagram",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Instagram API error: {response.status_code} - {response.text}",
                    "platform": "instagram",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error deleting Instagram post: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "platform": "instagram",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_post_stats(self, post_id: str) -> Dict[str, Any]:
        """Get statistics for an Instagram post.
        
        Args:
            post_id: ID of the post to get stats for
            
        Returns:
            Dictionary with statistics information
        """
        if not all([self.client_id, self.client_secret, self.access_token]):
            return {"success": False, "error": "Instagram API credentials not configured"}
        
        try:
            params = {
                "access_token": self.access_token,
                "fields": "insights.metric(engagement,impressions,reach,saved)"
            }
            
            response = requests.get(
                f"{self.api_url}/{post_id}",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                insights = data.get("insights", {}).get("data", [])
                
                stats = {}
                for metric in insights:
                    metric_name = metric.get("name")
                    metric_value = metric.get("values", [{}])[0].get("value", 0)
                    stats[metric_name] = metric_value
                
                return {
                    "success": True,
                    "stats": stats,
                    "platform": "instagram",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Instagram API error: {response.status_code} - {response.text}",
                    "platform": "instagram",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting Instagram post stats: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "platform": "instagram",
                "timestamp": datetime.utcnow().isoformat()
            } 