import os
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain.vectorstores.pgvector import PGVector
from langchain_anthropic import AnthropicEmbeddings
import logging
from langchain.vectorstores.pgvector import DistanceStrategy
from pydantic import BaseModel
import openai



logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        """Initialize the vector store with Anthropic embeddings and PGVector"""
        self.connection_string = os.getenv("NEON_CONNECTION_STRING")
        if not self.connection_string:
            raise ValueError("NEON_CONNECTION_STRING environment variable is required")

        self.embeddings = AnthropicEmbeddings()
        self.collection_name = "insurance_docs"
        self.embedding_model = "text-embedding-3-small"

    
    
    def init_store(self,documents:List,embeddings:List[AnthropicEmbeddings]) -> None:
        """
        Initialize PGVector store with initial embeddings and docs
        Args:
            embeddings(list): list of embeddings
            doc(list): list of documents (content and metadata)
        """
        logger.info("Initializing vector store")
        # Initialize PGVector store
        vector_store = PGVector.from_documents(
            embedding=embeddings,
            documents=documents,  # Your list of documents
            collection_name="your_collection_name",
            connection_string=self.connection_string,
            use_jsonb=True
        )
    

    

    def add_documents(self, documents: List[Document],embeddings:List[AnthropicEmbeddings]) -> None:
        """
        Add documents to existing vector store

        Args:
            documents: List of documents to add
        """
        logger.info(f"Adding {len(documents)} documents to vector store")

        

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        TODO: Perform similarity search

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of similar documents
        """
        logger.info(f"Performing similarity search for: {query}")
        # TODO: Implement similarity search
        db = PGVector.from_existing_index( 
            embedding=embeddings,
            documents=splits,
            collection_name=self.collection_name,
            connection_string=self.connection_string
        )
        
        similar = db.similarity_search_with_score(query, k=k)

        for doc in similar:
            print(doc, end="\n\n")
        return []

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main agent function to be called by the supervisor

        Args:
            state: Current state of the system

        Returns:
            Updated state
        """
        # TODO: Implement agent logic
        # Example:
        # 1. Check if there are new documents to store
        # 2. Add documents to vector store
        # 3. Update state with storage status
        return state
