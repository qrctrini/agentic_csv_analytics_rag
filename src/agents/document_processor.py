from typing import List, Dict, Any
from langchain_community.document_loaders import UnstructuredCSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain.agents import AgentExecutor, create_openai_tools_agent

from langgraph.prebuilt import create_react_agent
from loguru import logger
import logging
from pydantic import BaseModel
import os
import pathlib
import pandas as pd
from datetime import time
import json
import sys



# ---- project imports
from src.utils.utils import get_project_filepath, get_list_of_files_in_directory, load_config_params_for_node
from src.agents.vector_store import VectorStore


# setup loggers
logger_native = logging.getLogger(__name__)
logger.add(
    f"{get_project_filepath()}/logs/logfile.log",
    rotation=time(0, 0),
    format="{time} {level} {message}",
    level="DEBUG"
    )

class DocumentProcessor(BaseModel):
    name:str = "document_processor"
    role:str = "Document processor"
    next:str = "vector_store"
    task:str = "Send processed documents to the next node as a JSON list of dictionaries with keys : 'content','metadata'.Do NOT perform any analyis whatsever:"
    configs:dict = load_config_params_for_node(node="document_processor")
    text_splitter:RecursiveCharacterTextSplitter = None
    dir_path:str = f'{get_project_filepath()}/data'
    content_loaded_tracker:list = []
    vector_store:VectorStore = None
    
    class Config:
        arbitrary_types_allowed = True

    def setup(self) -> None:
        """
        - Initialize the text splitter using the current input variables
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.configs.get("chunk_size"),
            chunk_overlap=self.configs.get("chunk_overlap")
        )
       
    def get_filenames_from_folder(self,dir_path:str) -> list[str]: 
        """
        Get list of Excel files, filter for desirable characteristics

        Args:
            dirpath_path(str): Path to the Excel file

        Returns:
            files(list): List of files
        """
        files = []
        if dir_path:
            files = get_list_of_files_in_directory(dir_path=dir_path)
            files = [x for x in files if '.csv' in x.lower()]
        else:
            raise(f'There are no files to be found in {dir_path}')
        return files
        
    def load_csv(self, file_path: str) -> List[Document]:
        """
        Load CSV file

        Args:
            file_path: Path to the file

        Returns:
            List of Document objects
        """
        try:
            #logger.info(f"Loading Excel file: {file_path}")
            loader = UnstructuredCSVLoader(file_path)
            docs = loader.load()
            logger.info(f"Loaded: Excel file {file_path}={docs}")
        except FileNotFoundError:
            logger.error(f'Could not find {file_path}')
            docs = []
        except Exception as e:
            logger.error(f'Upstream error:{e}')
            docs = []
        return docs
    
    def load_all_files(self,dir_path:str) -> list[str]:
        """
        Load all files in director

        Args:
            dir_path: location of docments
              
        Returns:
            documents(list): loaded files split by textsplitter
        """
        files_to_load = get_list_of_files_in_directory(dir_path=dir_path)
        documents = []
        if files_to_load:
            logger.warning(f'files to load:{files_to_load}')
            for file_path in files_to_load:
                try:
                    # load and process files
                    file_path = f'{dir_path}/{file_path}'
                    documents += self.load_csv(file_path=file_path)
                except Exception as e:
                    logger.error(f'DocumentProcessor Error:{e}')
        logger.info(f'{len(files_to_load)}   ....  {len(documents)}')          
        return documents
            
    def load_df(self, df: pd.DataFrame) -> List[Document]:
        """
        Load dataframe

        Args:
            df: pandas DataFrame

        Returns:
            List of Document objects
        """
        try:
            if df is not None:
                # Concatenate all the columns into a string for each row
                texts = df.apply(lambda row: ' | '.join(row.astype(str)), axis=1).tolist()
                # Convert each row of text into a LangChain Document
                docs = [Document(page_content=text) for text in texts]
            raise('Load dataframe error: Dataframe is not loaded')

        except Exception as e:
            logger.error(f'Upstream error:{e}')
            docs = []
        return docs
    
    def process_documents(self, documents: List[Document]) -> List[Document]:
        """
        Process documents by splitting and extracting metadata

        Args:
            documents(list): raw documents

        Returns:
            docs(list): content with metadata
        """
        split_documents = []
        if documents:
            self.setup()
            docs = self.text_splitter.split_documents(documents)
            for doc in docs:
                if not isinstance(doc,str):
                    split_documents.append({"content":doc.page_content,"metadata":doc.metadata})
                    #split_documents += docs
        
        return split_documents
    
    def process_and_save_documents(self, documents: List[Document]) -> None:
        """
        Process documents by splitting and extracting metadata, then save to pgstore

        Args:
            documents(list): raw documents

        Returns:
            None
        """
        
        # -- process
        documents = self.process_documents(documents)
        if isinstance(documents[0],list):
            documents = documents[0]
        logger.info(f'documents:{documents}')
        # -- save
        try:
            if documents:
                if not self.vector_store:
                    self.vector_store = VectorStore()
                # delete all records
                self.vector_store.clear_store()
                self.vector_store.add_documents(documents=documents)
                return 'Documents successfully added'
        except Exception as e:
            logger.error(f'error saving documents:{e}')

    def query_llm(self, input_prompt:str=None):
        """Simulates querying the LLM with a role-specific prompt."""
        system=f"You are a: {self.name}. Your role: {self.role}. Your task: {self.function}."
        prompt = ""
        return prompt

    def run(self, state: str) -> Dict[str,list]:
        """
        Main agent function to be called by the supervisor

        Args:
            state(AgentState): Current state
              
        Returns:
            state message: Documents
        """
        logger.warning(f'state={state}')
        if state not in self.content_loaded_tracker:
            self.setup()
            documents = self.load_all_files(dir_path=state)
            processed_documents = self.process_documents(documents)
            #logger.warning(f'processed documents={processed_documents}')
            # memoize documents loaded this session
            self.content_loaded_tracker.append(state)
            #return {"documents": processed_documents}
            #processed_documents = ",  ".join(processed_documents)
            #return f"send to vector_store as a JSON object with keys : 'Year', 'Average expenditure', 'Percent change','metadata'.Do not perform any aggregations:{processed_documents}"
            #return f"send to Vector_store: {processed_documents}. DO NOT PERFORM ANALYSIS"
            #f"send documents to vector_store as a JSON list of dictionaries with keys : 'content','metadata'.Do NOT perform any analyis whatsoever.Documents:{processed_documents}",
            return {
                "messages":f"""goto vector_store.
                Send the processed documents as ONLY ONE big JSON array with keys : 'content','metadata':{processed_documents}.
                DO NOT PERFORM ANALYSIS in the vector_store_node.
                """,
                "next":self.next,
                "documents":processed_documents,
                "query":None,
                "dir_path":None
                }
        else:
            logger.warning(f"There are no documents to process")
            return {
                "messages":f"goto vector store.",
                "next":"vector_store",
                "documents":None,
                "query":None,
                "dir_path":None
                }
