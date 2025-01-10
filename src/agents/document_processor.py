from typing import List, Dict, Any
from langchain_community.document_loaders import UnstructuredExcelLoader, UnstructuredCSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from loguru import logger
import logging
from pydantic import BaseModel
import os
import pathlib
import pandas as pd

logger_native = logging.getLogger(__name__)

# ---- project imports
from src.utils.utils import get_project_filepath
from src.utils.agent_state import AgentState
    

class DocumentProcessor(BaseModel):
    chunk_size:int = 20
    chunk_overlap:int = 10
    text_splitter:RecursiveCharacterTextSplitter = None
    
    class Config:
        arbitrary_types_allowed = True

    def setup(self) -> None:
        """
        Perform setup actions:
        - create the text splitter using the current input variables
            
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        
    def load_csv(self, file_path: str) -> List[Document]:
        """
        Load Excel file using UnstructuredExcelLoader

        Args:
            file_path: Path to the Excel file

        Returns:
            List of Document objects
        """
        try:
            logger.info(f"Loading Excel file: {file_path}")
            loader = UnstructuredCSVLoader(file_path)
            docs = loader.load()
            logger.info(f"Loaded: csv file {file_path}={docs}")
        except FileNotFoundError:
            logger.error(f'Could not find {file_path}')
            docs = []
        except Exception as e:
            logger.error(f'Upstream error:{e}')
        return docs
    
    def process_documents(self, documents: List[Document]) -> tuple[Document,dict]:
        """
        Process documents by splitting and extracting metadata

        Args:
            documents(list): raw documents

        Returns:
            docs(list): content with metadata
        """
        docs = []
        if documents:
            docs = self.text_splitter.split_documents(documents)
            return docs
        return docs

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
        files_to_process = []
        for file_path,data in state.items():

            # load and process files
            documents = t.load_csv(file_path=file_path)
            docs = t.process_documents(documents=documents)

            # add dct to state
        return state


if __name__ == '__main__':
    t = DocumentProcessor()
    t.setup()
    #documents = t.load_csv(file_path=f'{get_project_filepath()}/data/expenditures_2012_2021.csv')

    