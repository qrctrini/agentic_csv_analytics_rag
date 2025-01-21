from loguru import logger
import os
import re
import json

# local imports
from src.agents.vector_store import VectorStore
from src.utils.utils import load_config_params_for_node, get_project_filepath


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
    except FileExistsError as e1:
        logger.error(f'file not found')
        files = f"Sorry there was an error finding files at path: {path} \n Maybe double check the path?"
    except Exception as e:
        logger.error(f'Error: {e}')

    logger.info(f"""
            csvs
    ----------------------
    {files}
    """)
    return files

def load_json_filedata(
        filepath:str=f'{get_project_filepath()}/data/output/analysis_node_output.json'
    ) -> dict:
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
            return data.get('analysis')
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

def delete_file(file_path:str) -> None:
    """
    Delete file
    Args:
        file_path: location of file on system
    Returns:
        -
    """
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info(f"The file {file_path} has been deleted.")
    else:
        logger.info(f"The file {file_path} does not exist.")



def from_dict_to_string_for_frontend_output(txt:dict) -> str:
    """
    Clean dict of strings for human readable output
    Args:
        txt: dictionary with text extracted from agent messages with poor formatting
    Returns:
        cleaned_data: cleaned string of output fit for human consumption
    """
    string = ''
    for key in range(1,10):
        text = txt.get(str(key))
        text = clean_string(text)
        logger.info(f'text={text}')
        string = f'{string}{text}'

        break
    return string

def clean_string(txt:str) -> str:
    """
    Replace non-human readable snippets in string
    Args:
        txt: block of text with e.g. backslashes etc
    Returns:
        txt: cleaned string of output fit for human consumption
    """
    logger.warning(f'text before clean:{txt}')
    if isinstance(txt,str):
        txt = txt.replace('Let me know if you need any other analysis on patterns in this data.',"")
    # txt=txt.replace('"',"").split('\\n\\n')
    # string = ""
    # for i in txt:
    #     string += f"\n{i}"
    # logger.info(f'cleaned string:{string}')
    # string=string.replace('\n',"")
    return txt

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

def update_config_file_with_chunk_size_chunk_overlap(chunk_size:int,chunk_overlap:int) -> None:
    """
    Update config with chunk size so it can be read document process

    Args:
        -chunk size: Size of token chunks
        -chunk overlap: Overlap of token chunks

    Returns:
        -
    """
    try:
        if isinstance(chunk_size,int) and isinstance(chunk_overlap,int):
            # load configs
            filepath = f'{get_project_filepath()}/src/config/config.json'
            with open(filepath,'r') as file:
                configs = json.load(file)
                configs["document_processor"]["chunk_size"]=chunk_size
                configs["document_processor"]["chunk_overlap"]=chunk_overlap

            # save updated configs
            json_data = json.dumps(configs,indent=4)
            with open(filepath,'w') as file:
                file.write(json_data)

            logger.info(f'config updated:{json_data}')
        else:
            logger.warning(f'Either overlap or size is wrong type: Overlap={type(chunk_overlap)} ... Size={type(chunk_size)}')

    except KeyError as e:
        logger.error(f'key error:{e}')
    except Exception as e:
        logger.error(f'error:{e}')


# if __name__ == '__main__':
#     output = load_json_filedata()
#     from_dict_to_string_for_frontend_output(output)