from loguru import logger
import os
import re
import json

# local imports
from src.agents.vector_store import VectorStore


def get_list_of_files(path:str) -> str:
    """
    Get a numerated string of files in a folder

    args:
        path(str): path to folder

    Return:
        files(str): numbered list of files
    """
    
    files = ""
    try:
        # Get the list of all files in a directory
        dirfiles = os.listdir(path)
        # add the files to list
        csvs = ""
        for idx,file in enumerate(dirfiles):
            idx += 1
            # Check if item is a file, not a directory
            if not os.path.isdir(os.path.join(path, file)):
                files += f"{idx}. {file}\n"
    except FileExistsError:
        logger.error(f'file not found')
        files = f"Sorry there was an error finding files at path: {csvs} \n Maybe double check the path?"

    logger.info(f"""
            csvs
    ----------------------
    {files}
    """)
    return files

def load_json_filedata(filepath:str='/tmp/analysis_node_response.json') -> dict:
    """
    Load json file from filepath and convert contents to dct
    Args:
        filepath: file location
    Returns:
        data: json file
    """
    try:
        with open(filepath,'r') as file:
            data = json.load(file)
            return data.get('analysis').get('analysis_node_response')
    except FileNotFoundError:
        logger.error(f'error:file not found at {filepath}')
    except Exception as e:
        logger.error(f'error:{e}')
    return None


def from_agent_message_string_to_human_readable_string(txt:str) -> str:
    """
    Clean dict of strings for human readable output
    Args:
        txt: block of text from agent messages with poor formatting
    Returns:
        cleaned_data: cleaned string of output fit for human consumption
    """
    dct = {}
    for i in range(1,10):
        j= i+ 1
        start,end = str(i), str(j)
        match = f'(?<=\"{start}\": ).*(?=\"{end}\": )'
        print(f'match={match}')
        pattern = re.compile(match)
        match = re.search(pattern,txt)
        dct[i] = clean_string(match.group())
        break
    return dct[i]

def clean_string(txt:str) -> str:
    """
    Replace non-human readable snippets in string
    Args:
        txt: block of text with e.g. backslashes etc
    Returns:
        txt: cleaned string of output fit for human consumption
    """
    logger.warning(f'text before clean:{txt}')
    txt=txt.replace('"',"").split('\\n\\n')
    string = ""
    for i in txt:
        string += f"\n{i}"
    logger.info(f'cleaned string:{string}')
    return string

def clear_vector_store() -> str:
    """
    Clear all documents from vector store

    Returns:
        vector store status update
    """
    vs = VectorStore()
    vs.clear_store()
    return 'Vector store emptied'

def get_vector_store_document_count() -> int:
    """
    Get count of documents in vector store

    Returns:
        # of docs in vector store
    """
    vs = VectorStore()
    return vs.get_document_count()

