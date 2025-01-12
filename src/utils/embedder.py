import openai
import pandas as pd
from pydantic import BaseModel
from typing import Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
import os
from functools import lru_cache
from loguru import logger
import os
from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings

load_dotenv()


class Embedder(BaseModel):
    model:str = "text-embedding-3-small"
    embedding:Any = None
    embedder:Any = None
    workers:int = 5
    FLAGS:dict= {
        'use_free_embedder':False,
    }
    openai_client:Any = None

    def initialize_openai_client(self) -> None:
        """
        Initialize the OPEN AI client
        """
        try:
            self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        except KeyError as e:
            logger.error(f"Error in getting_embedding: {e}")

    def get_embedding(self,text:str) -> list:
        """Generate an embedding for the given text using OpenAI's API."""
        # Check for valid input
        if not text or not isinstance(text, str):
            return None
        try:
            # Call OpenAI API to get the embedding
            response = self.openai_client.embeddings.create(
                input=text, 
                model=self.model,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error in getting_embedding: {e}")
            
            return None
    
    def threaded_embedder(self,documents:list[str]) -> list[list]:
        """
        Generate embeddings using threading for speedup
        args:
            documents(list): documents with metadata
        return:
            embeddings(list): list of embeddings
        """
        self.initialize_openai_client()
        futures,embeddings = [],[]
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            for doc in documents:
                futures.append(executor.submit(self.get_embedding,doc))

            for future in as_completed(futures):
                embeddings.append(future.result())
        
        return embeddings
    
    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Embedding function to be called by supervisor

        Args:
            state: Current state of the system

        Returns:
            Updated state
        """
        # TODO: Implement agent logic 
        # Example:
        # perform embeddings
        # 3. Update state with storage status
        return state



    
        
    