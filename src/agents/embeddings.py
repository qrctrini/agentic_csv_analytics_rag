import openai
import pandas as pd
from pydantic import BaseModel
from typing import Any
from concurrent.futures import ThreadPoolExecutor, as_completed

class MyEmbedder(BaseModel):
    model:str = None
    embedding:Any = None
    embedder:Any = None
    workers:int = 5

    def create_embeddings_from_input_text(self,text:str) -> dict:
        self.embedded = self.embedder(text=text,pretrained_model=self.inputs.model,inputs=self.inputs)

    def get_embedding(self,text:str) -> list:
        """Generate an embedding for the given text using OpenAI's API."""
        # Check for valid input
        if not text or not isinstance(text, str):
            return None
        try:
            # Call OpenAI API to get the embedding
            embedding = openai.embeddings.create(input=text, model=self.embedding_model).data[0].embedding
            return embedding
        except Exception as e:
            print(f"Error in get_embedding: {e}")
            return None
        
    def threaded_embedder(self,documents:list[Any]) -> list[list]:
        """
        Generate embeddings using threading for speedup
        args:
            documents(list): documents with metadata
        return:
            embeddings(list): list of embeddings
        """
        futures,embeddings = [],[]
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            for doc in documents:
                futures.append(executor.submit(self.get_embedding,doc.content))

            for future in as_completed(futures):
                embeddings.append(future.result())
        
        return embeddings
    

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
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



    
        
    