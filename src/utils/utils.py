import pathlib
from loguru import logger
import os
import pandas as pd
from bs4 import BeautifulSoup

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
    #df = pd.read_excel(original_filepath, sheet_name='Sheet1', header=0,engine='xlrd')
    #df = pd.read_html(original_filepath)
    filename = filename.split('.')[0]
    csv_filepath=f'{save_to_dir}/{filename}.csv'
    # read with html, get the 2nd table in the list of tables 
    tables = pd.read_html(original_filepath)
    df = tables[2]

    # Save the DataFrame to a CSV file
    df.to_csv(csv_filepath, index=False)
    
    logger.info(f'file saved to {csv_filepath}')

