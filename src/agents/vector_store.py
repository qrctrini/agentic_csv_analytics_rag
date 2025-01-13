import os
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_postgres.vectorstores import PGVector
from loguru import logger
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.pgvector import DistanceStrategy
from pydantic import BaseModel
from datetime import time
from dotenv import load_dotenv
load_dotenv()

# project imports
from src.utils.utils import get_project_filepath

# setup loggers
logger.add(
    f"{get_project_filepath()}/logs/logfile.log",
    rotation=time(0, 0),
    format="{time} {level} {message}",
    level="DEBUG"
    )

class VectorStore:
    def __init__(self):
        """Initialize the vector store with PGVector connection"""
        self.connection_string = os.getenv("NEON_CONNECTION_STRING")
        if not self.connection_string:
            raise ValueError("NEON_CONNECTION_STRING environment variable is required")

        self.collection_name:str = "insurance_docs"
        self.vector_store:PGVector = None
        self.embeddings = OpenAIEmbeddings()
        self.current_state_key:str = 'vector_store'
        self.next_state_key:str = 'insurance_analysis'

    def init_store(self) -> None:
        """
        Initialize PGVector store with initial embeddings and docs
        Args:
            embeddings(list): List of embeddings
            doc(list): List of text
            metadatas: List of metadatas associated with the texts.
        """
        try:
            logger.info("Initializing vector store")
            # Initialize PGVector store
            self.vector_store = PGVector(
                embeddings=self.embeddings,
                collection_name=self.collection_name,
                connection=self.connection_string,
                use_jsonb=True,
            )
           
            logger.info(f'store initialized')
        except IOError as e:
            logger.error(f'Error: problem writing embeddings to postgres vector store:{e}')

    def add_documents(self, documents: List[str]) -> None:
        """
        Add documents to existing vector store

        Args:
            documents: List of documents to add
        """
        logger.info(f"Adding {len(documents)} documents to vector store")
        # Adding embeddings with metadata
        if self.vector_store is None:
            self.init_store()
        # add documents
        self.vector_store.add_documents(documents)
            
    def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        """
        Perform similarity search

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of similar documents
        """
        logger.warning(f"Performing similarity search for: {query}")
        if self.vector_store is None:
            self.init_store()
       
        similar_docs = self.vector_store.similarity_search_with_score(query=query, k=k)
        return similar_docs

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
        if self.current_state_key in state:
            for file_path,documents in state[self.current_state_key].items():
                try:
                    # save documents
                    self.add_documents(documents=documents)
                    # update saved status
                    state[self.current_state_key][file_path]['saved_status'] = True
                except Exception as e:
                    logger.error(f'{self.current_state_key} Error:{e}')
        else:
            raise(f'{self.current_state_key} Error: files_to_process is not a key in state')
        return state
