import streamsync as ss
from streamsync.core import StreamsyncState
from loguru import logger
from datetime import datetime

# local imports
from frontend.utils import (
    get_list_of_files, 
    load_json_filedata, 
    from_agent_message_string_to_human_readable_string,
    get_vector_store_document_count,
    clear_vector_store,
    update_config_file_with_chunk_size_chunk_overlap,
    get_project_filepath,
    from_dict_to_string_for_frontend_output,
    delete_file

)
from src.agent import ragrunner

# non-frontend helpers
def _update_get_vector_store_document_count(state):
    count = get_vector_store_document_count()
    state['text_input_docs_in_vector_store'] = count
    
# -------------------------- start handlers ---------------------
def handle_clear_vector_store(state):
    clear_vector_store()

def handle_input_folder(state,payload):
    state["textarea_list_csvs"] = get_list_of_files(path=payload)

def handle_timer_display_analysis_tick(state:StreamsyncState):
    # handle analysis
    if state["SHOULD_SHOW_ANALYSIS"] == True:
        savepath = f'{get_project_filepath()}/data/output/analysis_node_output.json'
        text = load_json_filedata(filepath=savepath)
        #cleaned_text = from_agent_message_string_to_human_readable_string(txt=text)
        cleaned_text = from_dict_to_string_for_frontend_output(txt=text)
        state["textarea_show_analysis"] = cleaned_text
    else:
        state["textarea_show_analysis"] = f"No analysis to show right now (@ {datetime.now().__str__()})"

    # handle vector store count
    _update_get_vector_store_document_count(state)
    
def handle_analysis_display_options(state,payload):
    if "show_analysis" in payload:
        state["SHOULD_SHOW_ANALYSIS"]=True
    else:
        state["SHOULD_SHOW_ANALYSIS"]=False
    logger.info(f'{state["SHOULD_SHOW_ANALYSIS"]=}')

def handle_button_rag_runner(state):
    # debounce button 
    try:
        if 'running' not in state['text_input_runner_status'] :
            csv_folderpath = state['csv_folderpath']
            user_query = state['text_input_query']
            bullet_list_of_files = get_list_of_files(path=csv_folderpath)
            if 'Sorry there was an error' not in bullet_list_of_files:
                start = datetime.now()
                # set status update
                state["SHOULD_SHOW_ANALYSIS"] = False
                state['text_input_runner_status'] = f"Started running at {start.__str__()}"
                logger.warning(f'AGENTIC RAG STARTED')
                # start the rag
                ragrunner(csv_folderpath=csv_folderpath,query=user_query)
                end = datetime.now()
                timetaken = round((end - start).total_seconds()/60,1)
                # set status updated
                state['text_input_runner_status'] = f"Finished running at {end.__str__()}.\n Time taken(mins): {timetaken}"
                state["checkbox_analysis_display_options"] = ['show_analysis']
                state["SHOULD_SHOW_ANALYSIS"] = True
        else:
            logger.warning(f'CURRENTLY RUNNING')
    except Exception as e:
        logger.error(f'error:{e}')

def handle_button_run_query(state):
    logger.info(f'*************** inside run query only ***********************')
    try: 
        # debounce button 
        if 'running' not in state['text_input_runner_status'].lower() :
            user_query = state['text_input_query']
            documents_in_vector_store = state['text_input_docs_in_vector_store']
            if documents_in_vector_store > 0:
                start = datetime.now()
                # set status update
                state["SHOULD_SHOW_ANALYSIS"] = False
                state['text_input_runner_status'] = f"Started running at {start.__str__()}"
                logger.warning(f'AGENTIC RAG STARTED')
                # start the rag
                ragrunner(csv_folderpath=None,query=user_query)
                end = datetime.now()
                timetaken = round((end - start).total_seconds()/60,1)
                # set status updated
                state['text_input_runner_status'] = f"Finished last run at {end.__str__()}.\n Time taken(mins): {timetaken}"
                state["checkbox_analysis_display_options"] = ['show_analysis']
                state["SHOULD_SHOW_ANALYSIS"] = True
            else:
                logger.warning(f'Sorry cannot run query until there are documents in the vector store!')
                state['text_input_runner_status'] = f'Sorry there are no documents in the vector store so cannot run "query only". \nUse the Run RAG button to load documents and run the query after.'
        else:
            logger.warning(f'CURRENTLY RUNNING')
    except Exception as e:
        logger.error(f'error:{e}')


def handle_number_input_chunk_size(state,payload):
    logger.info(f'{type(payload)}...{payload}')
    state["number_input_chunk_size"]=int(payload)
    size = state["number_input_chunk_size"]
    overlap = state["number_input_chunk_overlap"]
    update_config_file_with_chunk_size_chunk_overlap(chunk_size=size,chunk_overlap=overlap)

def handle_number_input_chunk_overlap(state,payload):
    logger.info(f'{type(payload)}...{payload}')
    state["number_input_chunk_overlap"]=int(payload)
    size = state["number_input_chunk_size"]
    overlap = state["number_input_chunk_overlap"]
    update_config_file_with_chunk_size_chunk_overlap(chunk_size=size,chunk_overlap=overlap)

def handle_button_clear_analysis(state):
    delete_file(file_path=f'{get_project_filepath()}/data/output/analysis_node_output.json')
    state["textarea_show_analysis"] = "Nothing to show now"
    state["SHOULD_SHOW_ANALYSIS"] = False

# -------------------------- end handlers ---------------------
# Initialise the state
input_folder = f"{get_project_filepath()}/data/csv"
initial_state = ss.init_state({
    "my_app": {
        "title": "Agentic CSV Analytics RAG"
    },
    "_my_private_element": 1337,
    "message": None,
    "textarea_list_csvs":get_list_of_files(input_folder),
    "csv_folderpath":input_folder,
    "textarea_show_analysis":"Nothing to show now",
    "SHOULD_SHOW_ANALYSIS":False,
    "text_input_runner_status":"Ready!",
    "number_input_chunk_size":1000,
    "number_input_chunk_overlap":10,
    "text_input_query":"Perform in-depth analysis on the data in the vector store collection",
    "text_input_docs_in_vector_store":get_vector_store_document_count()
})

