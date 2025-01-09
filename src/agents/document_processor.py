from typing import List, Dict, Any
from langchain_community.document_loaders import UnstructuredExcelLoader, UnstructuredCSVLoader

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import logging
from pydantic import BaseModel
import os
import pathlib

logger = logging.getLogger(__name__)

# ---- project imports
from src.utils.utils import get_project_filepath

class DocumentProcessor(BaseModel):
    chunk_size:int = 1000
    chunk_overlap:int = 200
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

    def load_excel(self, file_path: str) -> List[Document]:
        """
        Load Excel file using UnstructuredExcelLoader

        Args:
            file_path: Path to the Excel file

        Returns:
            List of Document objects
        """
        logger.info(f"Loading Excel file: {file_path}")
        loader = UnstructuredExcelLoader(file_path,mode='elements')
        docs = loader.load()
        logger.info(f"Loaded: excel file {file_path}={docs}")
        return docs

    def process_documents(self, documents: List[Document]) -> List[Document]:
        """
        TODO: Process documents by splitting and extracting metadata

        Args:
            documents: List of raw documents

        Returns:
            List of processed Document objects
        """
        text = self.text_splitter.split_documents(self.text)
        logger.info(f"Processing {len(documents)} documents")
        # TODO: Implement document processing
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
        # 1. Check if there are Excel files to process
        # 2. Load and process documents
        # 3. Update state with processed documents
        return state


if __name__ == '__main__':
    t = DocumentProcessor()
    t.setup()
    t.load_excel(file_path=f'{get_project_filepath()}/data/expenditures_2012_2021.xls')