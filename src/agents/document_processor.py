from typing import List, Dict, Any
from langchain_community.document_loaders import UnstructuredExcelLoader, UnstructuredCSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from loguru import logger
import logging
from pydantic import BaseModel
import os
import pathlib

logger_native = logging.getLogger(__name__)

# ---- project imports
from src.utils.utils import get_project_filepath

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

        Args:
            file_path: Path to the Excel file

        Returns:
            List of Document objects
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
        logger.info(f"Loading Excel file: {file_path}")
        loader = UnstructuredCSVLoader(file_path)
        docs = loader.load()
        logger.info(f"Loaded: csv file {file_path}={docs}")
        return docs
    
    def process_documents(self, documents: List[Document]) -> tuple[Document,dict]:
        """
        Process documents by splitting and extracting metadata

        Args:
            documents(list): raw documents

        Returns:
            contents (list): lists of contents from document object
            content (list): list of metadata
        """
        docs = self.text_splitter.split_documents(documents)
        # split the content from the metadata
        content,metadata = [], []
        for doc in docs:
            content.append(doc.page_content)
            metadata.append(doc.metadata)
        return content, metadata

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
        # 1. Check if there are Excel files to process
        # 2. Load and process documents
        # 3. Update state with processed documents
        return state


if __name__ == '__main__':
    t = DocumentProcessor()
    t.setup()
    documents = t.load_csv(file_path=f'{get_project_filepath()}/data/expenditures_2012_2021.csv')
    content,metadata = t.process_documents(documents=documents)