import streamsync as ss
import os
# This is a placeholder to get you started or refresh your memory.
# Delete it or adapt it as necessary.
# Documentation is available at https://streamsync.cloud

# Shows in the log when the app starts
print("Hello world!")

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
    

def list_csvs(path:str) -> str:
    csvs = []
    # Get the list of all files in a directory
    files = os.listdir(path)
    # add the files to list
    csvs = set()
    for file in files:
        # Check if item is a file, not a directory
        if not os.path.isdir(os.path.join(path, file)):
            csvs.add(file)

    csvs = "; ".join(csvs)
    print(f"""
            csvs
    ----------------------
    {csvs}
    """)
    return csvs

def handle_input_folder(state,payload):
    state["textarea_list_csvs"] = list_csvs(payload)


# Initialise the state

# "_my_private_element" won't be serialised or sent to the frontend,
# because it starts with an underscore

initial_state = ss.init_state({
    "my_app": {
        "title": "My App"
    },
    "_my_private_element": 1337,
    "message": None,
    "textarea_list_csvs":list_csvs("/home/andre/workspace/aguide/projects/insurance_rag/insurance_analytic_rag/data/csv"),
    "counter":0,
    "input_folder":"/home/andre/workspace/aguide/projects/insurance_rag/insurance_analytic_rag/data/csv"
})

_update_message(initial_state)