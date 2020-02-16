import requests
import pytest

ROOT_URL='http://localhost:5000'

@pytest.fixture
def init_db(scope='session', autouse=True):
    print('INITING DB')
    from app import db, TaskModel
    for i in range(10):
        t = TaskModel(title='Task %s' % i)
        db.session.add(t)
    db.session.commit()
    yield db

def test_get_list_of_tasks():
    '''
        Check Get all Tasks Request
    '''
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
