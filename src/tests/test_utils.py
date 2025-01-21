import pytest
import os
import json
from loguru import logger
from unittest.mock import patch, mock_open

from src.utils.utils import get_project_filepath, save_dict_to_json_file, load_config_params_for_node


def test_get_project_path():
    project_path = get_project_filepath()
    root = os.path.dirname(os.path.abspath(__file__))
    # remove the /tests directory from the end 
    root = root.replace('/src/tests','')
    logger.info(f'root={root}')
    assert project_path == root


def test_save_dict_to_json_file(mocker):
    string = "my name is Jack"
    save_dict_to_json_file("my name is Jack","/tmp/jack")

    # get file
    with open('/tmp/jack.json','r') as file:
        json_data = json.loads(file)
    
    dct = dict(json_data)
    assert dct['analysis'] == string


def test_do_stuff_with_file():
    dct = {"1":"my name is Jack"}
    filepath = "/tmp/jack.json"
    open_mock = mock_open()
    with patch("builtins.open", open_mock, create=True):
        save_dict_to_json_file(dct,filepath)

    open_mock.assert_called_with(filepath, "w")
    open_mock.return_value.write.assert_called_once_with("test-data")

# def test_load_config_params_for_node():
#     config = load_config_params_for_node("analysis")
    
    