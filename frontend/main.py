import streamsync as ss

# local imports
from frontend.utils import get_list_of_files

# Its name starts with _, so this function won't be exposed
def _update_message(state):
    is_even = state["counter"] % 2 == 0
    message = ("+Even" if is_even else "-Odd")
    state["message"] = message


def decrement(state):
    state["counter"] -= 1
    _update_message(state)

def increment(state):
    state["counter"] += 1
    # Shows in the log when the event handler is run
    print("The counter has been incremented.")
    _update_message(state)
    

def handle_input_folder(state,payload):
    state["textarea_list_csvs"] = get_list_of_files(path=payload)

# Initialise the state
input_folder = "/home/andre/workspace/aguide/projects/insurance_rag/insurance_analytic_rag/data/csv"
initial_state = ss.init_state({
    "my_app": {
        "title": "My App"
    },
    "_my_private_element": 1337,
    "message": None,
    "textarea_list_csvs":get_list_of_files(input_folder),
    "counter":0,
    "input_folder":input_folder
})

_update_message(initial_state)