import requests
import pytest

ROOT_URL='http://localhost:5000'

def test_get_list_of_tasks():
    response = requests.get('{}/tasks/'.format(ROOT_URL))
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_specific_task():
    response = requests.get('{}/tasks/'.format(ROOT_URL))
    tasks = response.json()
    assert len(tasks) > 0
    random_task_id = tasks[0]['id']
    response = requests.get('{}/tasks/{}'.format(ROOT_URL, random_task_id))
    assert response.status_code == 200
    assert response.json()['id'] == random_task_id
