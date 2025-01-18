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
    clear_vector_store
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
        text = load_json_filedata(filepath='/tmp/analysis_node_response.json')
        cleaned_text = from_agent_message_string_to_human_readable_string(txt=text)
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
            bullet_list_of_files = get_list_of_files(path=csv_folderpath)
            if 'Sorry there was an error' not in bullet_list_of_files:
                start = datetime.now()
                # set status update
                state["SHOULD_SHOW_ANALYSIS"] = False
                state['text_input_runner_status'] = f"Started running at {start.__str__()}"
                logger.warning(f'AGENTIC RAG STARTED')
                # start the rag
                ragrunner(csv_folderpath=csv_folderpath)
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


# -------------------------- end handlers ---------------------
# Initialise the state
input_folder = "/home/andre/workspace/aguide/projects/insurance_rag/insurance_analytic_rag/data/csv"
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
    #"text_input_docs_in_vector_store":get_vector_store_document_count()
})

