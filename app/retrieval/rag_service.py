import logging
import os
from typing import Dict, List, Optional, Any, Tuple
import json
from sqlalchemy.orm import Session
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from app.models.content import ContentItem, ContentSource, ContentType
from app.config import settings

logger = logging.getLogger(__name__)

class RAGService:
    """RAG (Retrieval Augmented Generation) service for content retrieval."""
    
    def __init__(self, openai_api_key: Optional[str] = None, persist_directory: str = "data/vectorstore"):
        """Initialize the RAG service.
        
        Args:
            openai_api_key: OpenAI API key, defaults to settings
            persist_directory: Directory to persist vector store
        """
        api_key = openai_api_key or settings.OPENAI_API_KEY
        self.embeddings = OpenAIEmbeddings(api_key=api_key)
        self.persist_directory = persist_directory
        
        # Create the persist directory if it doesn't exist
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize the vector store
        self.vectorstore = None
        
    def _initialize_vectorstore(self):
        """Initialize the vector store if it exists."""
        try:
            if os.path.exists(self.persist_directory) and os.listdir(self.persist_directory):
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                logger.info(f"Loaded existing vector store from {self.persist_directory}")
            else:
                logger.info("No existing vector store found")
                self.vectorstore = None
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            self.vectorstore = None

    def index_content_items(self, content_items: List[ContentItem]) -> bool:
        """Index a list of content items in the vector store.
        
        Args:
            content_items: List of ContentItem objects to index
            
        Returns:
            Success status
        """
        try:
            texts = []
            metadatas = []
            ids = []
            
            # Process each content item
            for item in content_items:
                # Split the content into chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200,
                    separators=["\n\n", "\n", ". ", " ", ""]
                )
                
                # Get the document chunks
                chunks = text_splitter.split_text(item.content)
                
                # Add each chunk with metadata
                for i, chunk in enumerate(chunks):
                    texts.append(chunk)
                    metadatas.append({
                        "content_id": str(item.id),
                        "title": item.title,
                        "source_id": str(item.source_id),
                        "chunk_id": i,
                        "url": item.url
                    })
                    ids.append(f"{item.id}-{i}")
            
            if not texts:
                logger.warning("No content to index")
                return False
            
            # Create or update the vector store
            if self.vectorstore is None:
                self.vectorstore = Chroma.from_texts(
                    texts=texts,
                    embedding=self.embeddings,
                    metadatas=metadatas,
                    ids=ids,
                    persist_directory=self.persist_directory
                )
                self.vectorstore.persist()
                logger.info(f"Created new vector store with {len(texts)} chunks")
            else:
                self.vectorstore.add_texts(
                    texts=texts,
                    metadatas=metadatas,
                    ids=ids
                )
                self.vectorstore.persist()
                logger.info(f"Added {len(texts)} chunks to existing vector store")
            
            return True
            
        except Exception as e:
            logger.error(f"Error indexing content: {str(e)}")
            return False
    
    def retrieve_similar(self, query: str, limit: int = 5) -> List[Tuple[str, Dict[str, Any]]]:
        """Retrieve similar content chunks based on a query.
        
        Args:
            query: Query text to search for
            limit: Maximum number of results to return
            
        Returns:
            List of tuples (content_chunk, metadata)
        """
        try:
            if self.vectorstore is None:
                self._initialize_vectorstore()
                
            if self.vectorstore is None:
                logger.warning("No vector store available for retrieval")
                return []
            
            # Retrieve similar documents
            results = self.vectorstore.similarity_search_with_relevance_scores(
                query, k=limit
            )
            
            # Format results
            similar_items = []
            for doc, score in results:
                if score > 0.7:  # Only include reasonably similar items
                    similar_items.append((doc.page_content, doc.metadata))
            
            return similar_items
            
        except Exception as e:
            logger.error(f"Error retrieving similar content: {str(e)}")
            return []

    def add_content_item(self, content_item: ContentItem) -> None:
        """Add a content item to the vector store.
        
        Args:
            content_item: ContentItem to add
        """
        try:
            # Create document chunks
            chunks = self.text_splitter.split_text(content_item.content)
            
            # Create metadata for each chunk
            metadatas = []
            for i in range(len(chunks)):
                metadata = {
                    "content_item_id": content_item.id,
                    "source_id": content_item.source_id,
                    "title": content_item.title or "",
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
                
                # Add classification metadata if available
                if content_item.meta_data and "classification" in content_item.meta_data:
                    metadata.update({
                        "primary_category": content_item.meta_data["classification"].get("primary_category", ""),
                        "secondary_category": content_item.meta_data["classification"].get("secondary_category", ""),
                        "keywords": ", ".join(content_item.meta_data["classification"].get("keywords", [])),
                        "summary": content_item.meta_data["classification"].get("summary", "")
                    })
                
                metadatas.append(metadata)
            
            # Add documents to vector store
            ids = [f"content_{content_item.id}_chunk_{i}" for i in range(len(chunks))]
            self.vectorstore.add_texts(chunks, metadatas=metadatas, ids=ids)
            
            # Persist changes
            self.vectorstore.persist()
            logger.info(f"Added content item {content_item.id} to vector store")
            
        except Exception as e:
            logger.error(f"Error adding content item {content_item.id} to vector store: {str(e)}")
    
    def batch_add_content(self, content_items: List[ContentItem]) -> None:
        """Add multiple content items to the vector store.
        
        Args:
            content_items: List of ContentItem objects
        """
        for item in content_items:
            self.add_content_item(item)
    
    def retrieve(self, query: str, top_k: int = 5, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve relevant content based on a query.
        
        Args:
            query: Query string
            top_k: Number of results to retrieve
            filter_dict: Optional filter dictionary for metadata filtering
            
        Returns:
            List of retrieved documents with metadata
        """
        try:
            results = self.vectorstore.similarity_search_with_relevance_scores(
                query, k=top_k, filter=filter_dict
            )
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": score
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error retrieving content for query '{query}': {str(e)}")
            return []
    
    def retrieve_by_category(self, query: str, category: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve content filtered by category.
        
        Args:
            query: Query string
            category: Category to filter by
            top_k: Number of results to retrieve
            
        Returns:
            List of retrieved documents with metadata
        """
        filter_dict = {"primary_category": category}
        return self.retrieve(query, top_k, filter_dict) 