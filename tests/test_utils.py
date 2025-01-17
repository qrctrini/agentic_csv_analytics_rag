import pytest
import os
from src.utils.utils import get_project_filepath, save_dict_to_json_file, load_config_params_for_node
import json

def test_util_get_project_path():
    project_path = get_project_filepath()
    root = os.path.dirname(os.path.abspath(__file__))
    # remove the /tests directory from the end 
    root = root.replace('/tests','')
    assert project_path == root


def test_save_dict_to_json_file():
    string = "my name is Jack"
    save_dict_to_json_file("my name is Jack","/tmp/jack")

    # get 
    with open('/tmp/jack.json','r') as file:
        json_data = json.loads(file)
    
    dct = dict(json_data)
    assert dct['analysis'] == string


def test_load_config_params_for_node():
    config = load_config_params_for_node("analysis")
    
    