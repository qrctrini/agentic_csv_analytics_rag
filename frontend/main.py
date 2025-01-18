import streamsync as ss
from streamsync.core import StreamsyncState
from loguru import logger
from datetime import datetime

# local imports
from frontend.utils import (
    get_list_of_files, 
    load_json_filedata, 
    from_agent_message_string_to_human_readable_string
)
from src.agent import main
    
# -------------------------- handlers
def handle_input_folder(state,payload):
    state["textarea_list_csvs"] = get_list_of_files(path=payload)

def handle_timer_display_analysis_tick(state:StreamsyncState):
    if state["SHOULD_SHOW_ANALYSIS"] == True:
        text = load_json_filedata(filepath='/tmp/analysis_node_response.json')
        cleaned_text = from_agent_message_string_to_human_readable_string(txt=text)
        state["textarea_show_analysis"] = cleaned_text
    else:
        state["textarea_show_analysis"] = f"No analysis to show right now (@ {datetime.now().__str__()})"

def handle_analysis_display_options(state,payload):
    if "show_analysis" in payload:
        state["SHOULD_SHOW_ANALYSIS"]=True
    else:
        state["SHOULD_SHOW_ANALYSIS"]=False
    logger.info(f'{state["SHOULD_SHOW_ANALYSIS"]=}')

# Initialise the state
input_folder = "/home/andre/workspace/aguide/projects/insurance_rag/insurance_analytic_rag/data/csv"
initial_state = ss.init_state({
    "my_app": {
        "title": "Agentic CSV Analytics RAG"
    },
    "_my_private_element": 1337,
    "message": None,
    "textarea_list_csvs":get_list_of_files(input_folder),
    "counter":0,
    "input_folder":input_folder,
    "textarea_show_analysis":"Nothing to show now",
    "SHOULD_SHOW_ANALYSIS":False
})

