from loguru import logger
import os

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
        files = os.listdir(path)
        # add the files to list
        csvs = ""
        for idx,file in enumerate(files):
            idx += 1
            # Check if item is a file, not a directory
            if not os.path.isdir(os.path.join(path, file)):
                files += f"{idx}. {file}\n"
    except FileExistsError:
        logger.error(f'file not found')
        files = f"Sorry there was an error finding files at path: {csvs} \n Maybe double check the path?"

    #csvs = "; ".join(csvs)
    print(f"""
            csvs
    ----------------------
    {files}
    """)
    return files

