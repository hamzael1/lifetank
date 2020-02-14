import requests
import pytest

ROOT_URL='http://localhost:5000'

def test_get_list_of_tasks():
    response = requests.get('{}/tasks/'.format(ROOT_URL))
    assert response.status_code == 200

def test_get_specific_task():
    response = requests.get('{}/tasks/{}'.format(ROOT_URL, 1))
    assert response.status_code == 200
