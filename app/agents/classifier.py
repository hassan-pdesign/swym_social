import json
import logging
from typing import Dict, List, Optional, Any
from app.models.content import ContentItem
from app.config import settings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

logger = logging.getLogger(__name__)

class ContentClassifier:
    """Agent for classifying content into categories."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the content classifier.
        
        Args:
            openai_api_key: OpenAI API key, defaults to settings
        """
        api_key = openai_api_key or settings.OPENAI_API_KEY
        self.llm = ChatOpenAI(
            model="gpt-4-turbo",
            temperature=0,
            api_key=api_key
        )
        
        self.classification_prompt = ChatPromptTemplate.from_template("""
        You are a content classification expert tasked with categorizing content for a social media management system.
        
        Please analyze the following content and categorize it according to these categories:
        - product: Content about specific products, features, or services
        - case_study: Content about case studies, success stories, or implementations
        - industry: Content about industry trends, statistics, or analysis
        - company: Content about the company, team, or culture
        - educational: Content that educates or teaches users about a topic
        - promotional: Content that promotes events, webinars, or special offers
        
        Additionally, extract relevant keywords (up to 5) that represent the main topics of the content.
        
        Content:
        ```
        {content}
        ```
        
        Respond with a JSON object with the following structure:
        {{"primary_category": "category_name", 
          "secondary_category": "category_name",
          "keywords": ["keyword1", "keyword2", "..."], 
          "summary": "A brief 1-2 sentence summary of the content",
          "confidence": 0.XX // a value between 0 and 1
        }}
        """)
        
        self.classification_chain = LLMChain(
            llm=self.llm,
            prompt=self.classification_prompt
        )
    
    def classify_content(self, content_item: ContentItem) -> Dict[str, Any]:
        """Classify a content item.
        
        Args:
            content_item: The ContentItem to classify
            
        Returns:
            Dict with classification results
        """
        try:
            # If the content is too long, truncate it
            content = content_item.content
            if len(content) > 8000:
                content = content[:8000] + "..."
            
            # Get classification from LLM
            result = self.classification_chain.invoke({"content": content})
            
            # Parse the JSON response
            classification = json.loads(result["text"])
            
            # Update content_item meta_data with classification
            if content_item.meta_data:
                meta_data = content_item.meta_data
            else:
                meta_data = {}
                
            meta_data.update({
                "classification": {
                    "primary_category": classification.get("primary_category"),
                    "secondary_category": classification.get("secondary_category"),
                    "keywords": classification.get("keywords", []),
                    "summary": classification.get("summary"),
                    "confidence": classification.get("confidence", 0.0)
                }
            })
            
            return classification
            
        except Exception as e:
            logger.error(f"Error classifying content item {content_item.id}: {str(e)}")
            return {
                "primary_category": "unknown",
                "secondary_category": "unknown",
                "keywords": [],
                "summary": "Error during classification",
                "confidence": 0.0
            }
    
    def batch_classify(self, content_items: List[ContentItem]) -> Dict[int, Dict[str, Any]]:
        """Classify multiple content items.
        
        Args:
            content_items: List of ContentItem objects
            
        Returns:
            Dict mapping content item IDs to classification results
        """
        results = {}
        
        for item in content_items:
            classification = self.classify_content(item)
            results[item.id] = classification
            
        return results 