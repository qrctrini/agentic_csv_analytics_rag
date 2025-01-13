from typing import List, Dict, Any
from langchain_community.document_loaders import UnstructuredExcelLoader, UnstructuredCSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, CSVTextSplitter
from langchain_core.documents import Document
from loguru import logger
import logging
from pydantic import BaseModel
import os
import pathlib
import pandas as pd
from datetime import time

# ---- project imports
from src.utils.utils import get_project_filepath, get_list_of_files_in_directory
from src.utils.agent_state import AgentState
from src.utils.agent_state import State

# setup loggers
logger_native = logging.getLogger(__name__)
logger.add(
    f"{get_project_filepath()}/logs/logfile.log",
    rotation=time(0, 0),
    format="{time} {level} {message}",
    level="DEBUG"
    )

class DocumentProcessor(BaseModel):
    chunk_size:int = 50
    chunk_overlap:int = 10
    text_splitter:CSVTextSplitter
    dir_path:str = f'{get_project_filepath()}/data'
    
    current_state_key:str = 'document_processor'
    next_state_key:str = 'vector_store'
    
    class Config:
        arbitrary_types_allowed = True

    def setup(self) -> None:
        """
        - Initialize the text splitter using the current input variables
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
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
        Load Excel file using UnstructuredExcelLoader

        Args:
            file_path: Path to the Excel file

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
                    split_documents.append(doc)
                    
            return split_documents
        return split_documents

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main agent function to be called by the supervisor

        Args:
            state(AgentState): Current state
              
        Returns:
            Updated state
        """
        # Example:
        # 1. Check if there are Excel files to process
        if self.current_state_key in state:
            for file_path in state[self.current_state_key]:
                try:
                    # load and process files
                    loaded_documents = self.load_csv(file_path=file_path)
                    processed_documents = self.process_documents(documents=loaded_documents)
                    # update state with documents to process
                    state[self.next_state_key][file_path] = {'documents':processed_documents,'saved_status':False}
                    # remove processed file from filepath
                    state[self.current_state_key].remove(file_path)
                except Exception as e:
                    logger.error(f'DocumentProcessor Error:{e}')
        else:
            raise('DocumentProcessor Error: files_to_process is not a key in state')

        return state


    