import os
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_postgres.vectorstores import PGVector
from loguru import logger
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.pgvector import DistanceStrategy
from langchain.indexes import SQLRecordManager, index
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel
from datetime import time
import ast
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

        # -- managing upserts
        self.namespace = f"pgvector/{self.connection_string}"
        self.record_manager = SQLRecordManager(
            self.namespace, db_url=self.connection_string
        )

       
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
    
    def clear_store(self):
        try:
            self.init_store()
            self.vector_store.delete_collection()
            logger.info(f'Vector Store Cleared!')
        except IOError as e:
            logger.error(f'Clear vector store error:{e}')
        
    def add_documents(self, documents: List[Document]) -> None:
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
        documents_added = self.vector_store.add_documents(documents)

        # -- for upserting
        # index(docs, record_manager, vectorstore, cleanup="incremental", source_id_key="source"))

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
        if self.vector_store is None:
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
                # with ThreadPoolExecutor as executor:
                #     futures = []
                #     for item in state:
                #         futures.append(executor.submit(self.convert_item_to_document,item))
                #     for future in as_completed(futures):
                #         inserted_counter += 1
                #         logger.info(f'inserted_counter={inserted_counter}')


            return {
                "messages":'Goto analysis node: You are a data analyst.Perform in depth analyis using all the data using the analysis retreiver',
                "next":"analysis",
                "documents":None,
                "dir_path":None}
 
                
        else:
            return {
                "messages":'Data in wrong format',
                "next":""
            }
