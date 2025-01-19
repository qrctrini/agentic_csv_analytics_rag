import os
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_postgres.vectorstores import PGVector
from loguru import logger
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.pgvector import DistanceStrategy
from datetime import time
import ast
from sqlalchemy.orm import Session
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

       
    def init_store(self) -> None:
        """
        Initialize PGVector store with initial embeddings and docs
        Args:
            embeddings(list): List of embeddings
            doc(list): List of text
            metadatas: List of metadatas associated with the texts.
        """
        try:
            if self.vector_store is None:
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
    
    def clear_store(self):
        """
        clear all documents from existing vector store
        """
        try:
            self.init_store()
            self.vector_store.delete_collection()
            logger.info(f'Vector Store Cleared!')
        except IOError as e:
            logger.error(f'Clear vector store error:{e}')

    def get_document_count(self) -> int:
        """
        Count documents in vector store

        Returns:
            count: # number of document in vector store
        """
        self.init_store()
        with Session(self.vector_store.session_maker.bind) as session:
            count = session.query(self.vector_store.EmbeddingStore).count()
        return count
        
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to existing vector store

        Args:
            documents: List of documents to add
        """
        logger.info(f"Adding {len(documents)} documents to vector store")
        # Adding embeddings with metadata
        self.init_store()
        # add documents
        documents_added = self.vector_store.add_documents(documents)
        return documents_added
            
    def similarity_search(self, query: str, k: int = 500) -> List[Document]:
        """
        Perform similarity search

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of similar documents
        """
        logger.warning(f"Performing similarity search for: {query}")
        self.init_store()
       
        similar_docs = self.vector_store.similarity_search_with_score(query=query, k=k)
        return similar_docs
    
    def convert_item_to_document(self,item):
        content,metadata=item['content'],item['metadata']
        #logger.info(f'content={content}, metadata={metadata}')
        # save documents
        document = Document(page_content=content,metadata=metadata)
        documents_added = self.add_documents(documents=[document])
        return documents_added

    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main agent function to be called by the supervisor

        Args:
            state: Current state of the system

        Returns:
            Updated state
        """
        logger.info(f'++++{type(state)} ---  state={state}')
        if isinstance(state,str):
            state = ast.literal_eval(state)
            logger.warning(f'{type(state)}****state:{state}')
            if isinstance(state,list):
                inserted_counter = 0
                documents = []
                for item in state:
                    try:
                        content,metadata=item['content'],item['metadata']
                        #logger.info(f'content={content}, metadata={metadata}')
                        # save documents
                        documents.append(Document(page_content=content,metadata=metadata))
                        documents_added = self.add_documents(documents=documents)
                        inserted_counter += len(documents)
                    except Exception as e:
                        logger.error(f'Vector store Error:{e}')
            return {
                "messages":"""Goto analysis node: 
                You are a data analyst.Perform in depth analyis after retrieving the data using the analysis tool.
                The data has three columns: [Year, Average expenditure, Percent change].
                Use the PythonREPL tool to use pandas to find trends, outliers, anomalies, and predictions.
                Do not make up information that isn't in the dataset.
                """,
                "next":"analysis",
                "documents":None,
                "dir_path":None}
        else:
            return {
                "messages":'Data in wrong format',
                "next":"vector_store"
            }


