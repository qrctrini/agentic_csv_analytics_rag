import pathlib
from loguru import logger
import os
import pandas as pd
import json
from datetime import datetime
from typing import Optional, Union

def get_project_filepath() -> str:
    """
    Get filepath of project directory from the utils file
    Args:
        -
    Returns:
        filepath(str): filepath of project directory
    """
    filepath = str(pathlib.Path(__file__).parent.parent.parent.resolve())
    return filepath

def get_list_of_files_in_directory(dir_path:str=None) -> list[str]:
    """
    Get list of files in directory
    Args:
        dirpath(str): path of directory
        
    Returns:
        files(list): list of filenames
        
    """
    # Get list of only files in the directory
    files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    return files 

def convert_excel_to_csv(dir_path:str,filename:str,save_to_dir:str) -> None:
    """
    Convert xls file to csv file and save to specified directory
    Args:
        dir_path(str): path of directory
        filename(str): filename
        
    Returns:
        -
    """
    original_filepath=f'{dir_path}/{filename}'
    filename = filename.split('.')[0]
    csv_filepath=f'{save_to_dir}/{filename}.csv'
    # read with html, grab the 2nd table in the list of tables 
    tables = pd.read_html(original_filepath)
    df = tables[2]

    # Save the DataFrame to a CSV file
    df.to_csv(csv_filepath, index=False)
    
    logger.info(f'file saved to {csv_filepath}')

def save_dict_to_json_file(dct:dict,dir_path:str) -> None:
    """
    Save string to json file

    Args:
        dct(dict): dictionary
        dir_path(str): save path of directory
         
    Returns:
        -
    """
    try:
        # pop .json if appended
        dir_path = dir_path.replace('.json','')
        dir_path = f'{dir_path}.json'
        json_data = json.dumps({
            "timestamp":datetime.now().__str__(),
            "analysis":dct,
            })
        with open(dir_path,'w') as file:
            file.write(json_data)
            logger.info(f'file written to {dir_path}')

    except FileNotFoundError as e:
        logger.error(f'error:{e}')
    except Exception as e1:
        logger.error(f'error:{e1}')


def load_config_params_for_node(node:str) -> Union[dict,str]:
    """
    Load the config for a node from the config file at src.config

    Args:
        dct(dict): dictionary
        dir_path(str): save path of directory
         
    Returns:
        config: config from a particular node corresponding
    """
    try:
        with open(f'{get_project_filepath()}/src/config/config.json','r') as file:
            dct = json.load(file) 
            return dct.get(node,None)
    except FileNotFoundError as e:
        logger.error(f'error:{e}')
        return None
    except KeyError as e:
        logger.error(f'error:{e}')
        return None

   