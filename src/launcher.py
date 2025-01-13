from src.agents.document_processor import DocumentProcessor
from src.utils.embedder import Embedder
from src.agents.vector_store import VectorStore
from pydantic import BaseModel
from src.utils.utils import get_project_filepath, get_list_of_files_in_directory,\
    convert_excel_to_csv
from datetime import time,datetime
from loguru import logger
logger.add(
    f"{get_project_filepath()}/logs/logfile.log",
    rotation=time(0, 0),
    format="{time} {level} {message}",
    level="DEBUG"
    )


class Launcher(BaseModel):
    """
    Launch the agents in sequence
    """

    def apply(self):
        """
        Launch the agents in sequence
        """
        # process the documents with text splitter
        d = DocumentProcessor()
        dir_path = f'{get_project_filepath()}/data/csv'
        filenames = d.get_filenames_from_folder(dir_path)
        logger.info(f'files={filenames}')
        start = datetime.now()
        # save to vector store
        vs = VectorStore()
        for filename in filenames:
            documents = d.load_csv(file_path=f'{dir_path}/{filename}')
            documents = d.process_documents(documents=documents)
            #vs.add_documents(documents=documents)
        
        #save to store
        #logger.warning(f'load and process conversion time (secs)={(datetime.now() - start).total_seconds()}')

        # save to store
        # vs = VectorStore()
        # vs.similarity_search(query='What are the trends in the data?',k=2)

        
        

if __name__ == '__main__':
    l = Launcher()
    l.apply()
