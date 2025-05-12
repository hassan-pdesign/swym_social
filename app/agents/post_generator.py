import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from app.models.content import ContentItem, Post, Platform, ContentStatus
from app.config import settings
from app.retrieval.rag_service import RAGService
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

logger = logging.getLogger(__name__)

class PostGenerator:
    """Agent for generating social media posts."""
    
    def __init__(self, openai_api_key: Optional[str] = None, rag_service: Optional[RAGService] = None):
        """Initialize the post generator.
        
        Args:
            openai_api_key: OpenAI API key, defaults to settings
            rag_service: RAG service for content retrieval
        """
        api_key = openai_api_key or settings.OPENAI_API_KEY
        self.llm = ChatOpenAI(
            model="gpt-4-turbo",
            temperature=0.7,
            api_key=api_key
        )
        
        self.rag_service = rag_service
        
        # LinkedIn post generation prompt
        self.linkedin_prompt = ChatPromptTemplate.from_template("""
        You are a professional social media content creator for a B2B technology company.
        Your task is to create an engaging LinkedIn post based on the provided content.
        
        LinkedIn posts should be professional, insightful, and provide value to the reader.
        They should be conversational but maintain a professional tone.
        
        Content to base the post on:
        ```
        {content}
        ```
        
        Keywords: {keywords}
        Category: {category}
        Brand Voice: {brand_voice}
        
        Follow these guidelines:
        - Write in a clear, professional tone
        - Start with a strong hook
        - Include 2-3 relevant hashtags
        - Keep the post between 150-280 words
        - Include a clear call-to-action
        - Avoid excessive use of emojis (1-2 max)
        - Format the post with line breaks for readability
        - Do not include "Hashtags:" or similar labels before the hashtags
        
        Create a LinkedIn post that will engage professionals in the industry.
        """)
        
        # Twitter post generation prompt
        self.twitter_prompt = ChatPromptTemplate.from_template("""
        You are a professional social media content creator for a B2B technology company.
        Your task is to create an engaging Twitter post based on the provided content.
        
        Twitter posts should be concise, impactful, and attention-grabbing.
        
        Content to base the post on:
        ```
        {content}
        ```
        
        Keywords: {keywords}
        Category: {category}
        Brand Voice: {brand_voice}
        
        Follow these guidelines:
        - Keep the post under 280 characters
        - Start with a compelling hook
        - Include 1-2 relevant hashtags
        - Use a conversational tone
        - Include a clear call-to-action when appropriate
        - Use at most 1 emoji
        - Do not include "Hashtags:" or similar labels before the hashtags
        
        Create a Twitter post that will drive engagement and shares.
        """)
        
        # Instagram post generation prompt
        self.instagram_prompt = ChatPromptTemplate.from_template("""
        You are a professional social media content creator for a B2B technology company.
        Your task is to create an engaging Instagram post caption based on the provided content.
        
        Instagram captions should be visually descriptive, engaging, and include a strong call-to-action.
        
        Content to base the post on:
        ```
        {content}
        ```
        
        Keywords: {keywords}
        Category: {category}
        Brand Voice: {brand_voice}
        
        Follow these guidelines:
        - Start with a strong visual description or hook
        - Keep the caption between 125-200 words
        - Include 3-5 relevant hashtags at the end
        - Use a friendly, approachable tone
        - Include a clear call-to-action
        - Use line breaks for readability
        - Use 1-3 relevant emojis to enhance the message
        - Do not include "Hashtags:" or similar labels before the hashtags
        
        Create an Instagram caption that will complement a visual and drive engagement.
        """)
        
        # Chain for each platform
        self.linkedin_chain = LLMChain(llm=self.llm, prompt=self.linkedin_prompt)
        self.twitter_chain = LLMChain(llm=self.llm, prompt=self.twitter_prompt)
        self.instagram_chain = LLMChain(llm=self.llm, prompt=self.instagram_prompt)
    
    def generate_post(self, content_item: ContentItem, platform: Platform, brand_voice: str = "professional") -> Post:
        """Generate a social media post for a specific platform.
        
        Args:
            content_item: ContentItem to generate post from
            platform: Platform to generate post for
            brand_voice: Brand voice to use
            
        Returns:
            Post object with generated content
        """
        try:
            # Get keywords and category from content meta_data
            keywords = []
            category = "general"
            
            if content_item.meta_data and "classification" in content_item.meta_data:
                classification = content_item.meta_data["classification"]
                keywords = classification.get("keywords", [])
                category = classification.get("primary_category", "general")
            
            # Format keywords for prompt
            keywords_str = ", ".join(keywords) if keywords else "technology, innovation"
            
            # Prepare parameters
            params = {
                "content": content_item.content[:5000] if len(content_item.content) > 5000 else content_item.content,
                "keywords": keywords_str,
                "category": category,
                "brand_voice": brand_voice
            }
            
            # Generate post based on platform
            if platform == Platform.LINKEDIN:
                result = self.linkedin_chain.invoke(params)
                text_content = result["text"]
            elif platform == Platform.TWITTER:
                result = self.twitter_chain.invoke(params)
                text_content = result["text"]
            elif platform == Platform.INSTAGRAM:
                result = self.instagram_chain.invoke(params)
                text_content = result["text"]
            else:
                # Default to LinkedIn if platform not supported
                result = self.linkedin_chain.invoke(params)
                text_content = result["text"]
            
            # Create Post object
            post = Post(
                content_item_id=content_item.id,
                text_content=text_content,
                status=ContentStatus.DRAFT,
                platform=platform,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                meta_data={
                    "generated_with": f"gpt-4-turbo",
                    "platform": platform.value,
                    "keywords": keywords,
                    "category": category,
                    "brand_voice": brand_voice
                }
            )
            
            return post
            
        except Exception as e:
            logger.error(f"Error generating post for content item {content_item.id}: {str(e)}")
            # Return a generic error post
            return Post(
                content_item_id=content_item.id,
                text_content=f"Error generating post: {str(e)}",
                status=ContentStatus.DRAFT,
                platform=platform,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                meta_data={
                    "error": str(e)
                }
            )
    
    def generate_for_all_platforms(self, content_item: ContentItem, brand_voice: str = "professional") -> Dict[Platform, Post]:
        """Generate posts for all supported platforms.
        
        Args:
            content_item: ContentItem to generate posts from
            brand_voice: Brand voice to use
            
        Returns:
            Dict mapping platforms to generated Post objects
        """
        results = {}
        
        for platform in [Platform.LINKEDIN, Platform.TWITTER, Platform.INSTAGRAM]:
            post = self.generate_post(content_item, platform, brand_voice)
            results[platform] = post
        
        return results
    
    def generate_with_rag(self, query: str, platform: Platform, brand_voice: str = "professional") -> Tuple[Post, List[Dict[str, Any]]]:
        """Generate a post using the RAG service for relevant content retrieval.
        
        Args:
            query: Query to retrieve relevant content
            platform: Platform to generate post for
            brand_voice: Brand voice to use
            
        Returns:
            Tuple of (generated Post, list of retrieved documents)
        """
        if not self.rag_service:
            raise ValueError("RAG service not provided")
        
        # Retrieve relevant content
        retrieved_docs = self.rag_service.retrieve(query, top_k=3)
        
        if not retrieved_docs:
            raise ValueError(f"No content found for query: {query}")
        
        # Combine retrieved content
        combined_content = "\n\n".join([doc["content"] for doc in retrieved_docs])
        
        # Create a temporary ContentItem for generation
        temp_content_item = ContentItem(
            id=-1,  # Temporary ID
            source_id=-1,  # Temporary source ID
            title=query,
            content=combined_content,
            ingested_at=datetime.utcnow(),
            meta_data={
                "classification": {
                    "primary_category": "general",
                    "secondary_category": "general",
                    "keywords": query.split(),
                    "summary": query
                }
            }
        )
        
        # Generate post
        post = self.generate_post(temp_content_item, platform, brand_voice)
        
        return post, retrieved_docs 