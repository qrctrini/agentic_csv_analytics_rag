import pathlib
from loguru import logger

def get_project_filepath() -> str:
    """
    Get filepath of project directory from the utils file
    
    Args:
        
    Returns:
        filepath (str): filepath of project directory
    """
    filepath = str(pathlib.Path(__file__).parent.parent.parent.resolve())
    logger.info(f'project filepath={filepath}, {type(filepath)}')
    return filepath
