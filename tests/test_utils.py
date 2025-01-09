import pytest
import os
from src.utils.utils import get_project_filepath


def test_util_get_project_path():
    project_path = get_project_filepath()
    root = os.path.dirname(os.path.abspath(__file__))
    # remove the /tests directory from the end 
    root = root.replace('/tests','')
    assert project_path==root