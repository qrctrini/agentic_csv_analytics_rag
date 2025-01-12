from src.agents.document_processor import DocumentProcessor
from src.utils.embedder import Embedder
from src.agents.vector_store import VectorStore
from pydantic import BaseModel
from src.utils.utils import get_project_filepath
from loguru import logger

class Launcher(BaseModel):
    """
    Launch the agents in sequence
    """

    def apply(self):
        """
        Launch the agents in sequence
        """
        # process the documents with text splitter
        # d = DocumentProcessor()
        # documents = d.load_csv(file_path=f'{get_project_filepath()}/data/expenditures_2012_2021.csv')
        # documents,metadatas = d.process_documents(documents=documents)
        # # create embeddings
        # e = Embedder()
        # embeddings = e.threaded_embedder(documents)
        #logger.info(f'''embeddings={embeddings[:1]}''')

        # save to store
        # vs = VectorStore()
        # vs.add_documents(documents=documents, metadatas=metadatas,embeddings=None)

        # save to store
        vs = VectorStore()
        vs.similarity_search(query='What are the trends in the data?',k=2)

if __name__ == '__main__':
    l = Launcher()
    l.apply()
