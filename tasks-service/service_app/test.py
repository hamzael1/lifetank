import requests
import pytest
from sqlalchemy.sql.expression import func

from app import app
from model import db, TaskModel

from datetime import datetime
from random import random as rand, randrange

ROOT_URL='http://localhost:5000'

LOGIN_URL='http://localhost:8888/auth/login/'

@pytest.fixture(scope='session', autouse=False)
def test_user_1():
    return {
        'id': 1000,
        'username': 'test_user_1',
        'password': 'test_pass'
    }

@pytest.fixture(scope='session', autouse=False)
def test_user_2():
    return {
        'id': 1001,
        'username': 'test_user_2',
        'password': 'test_pass'
    }

NBR_TASKS_PER_USER = 10
NBR_USERS = 2

def populate_db(user_1_id, user_2_id):
    with app.app_context():
        db.drop_all()
        db.create_all()
        for i in range(NBR_TASKS_PER_USER):
            t = TaskModel (
                    title='Task Test {}'.format(i+1),
                    user_id=user_1_id,
                    comment='Comment for Task Test {}'.format(i+1),
                    done=True if rand() > 0.5 else False,
                    due=datetime(2020,randrange(2,6), randrange(1,26))
                )
            db.session.add(t)
        db.session.commit()
        for i in range(NBR_TASKS_PER_USER):
            t = TaskModel (
                    title='Task Test {}'.format(i+1),
                    user_id=user_1_id,
                    comment='Comment for Task Test {}'.format(i+1),
                    done=True if rand() > 0.5 else False,
                    due=datetime(2020,randrange(2,6), randrange(1,26))
                )
            db.session.add(t)
        db.session.commit()

@pytest.fixture(scope='module', autouse=True)
def init_db_for_test_session(request, test_user_1, test_user_2):
    db.init_app(app)
    populate_db(test_user_1['id'], test_user_2['id'])
    def fin():
        with app.app_context():
            db.drop_all()
    request.addfinalizer(fin)

@pytest.fixture(scope='module', autouse=False)
def token_user_1(test_user_1):
    response = requests.post(LOGIN_URL, json={
            'username': test_user_1['username'],
            'password': test_user_1['password'],
        })
    assert response.status_code == 200
    resp_body = response.json()
    assert response.status_code == 200 and 'access_token' in resp_body
    token = resp_body['access_token']
    return token

@pytest.fixture(scope='module', autouse=False)
def token_user_2(test_user_2):
    response = requests.post(LOGIN_URL, json={
            'username': test_user_2['username'],
            'password': test_user_2['password'],
        })
    assert response.status_code == 200
    resp_body = response.json()
    assert response.status_code == 200 and 'access_token' in resp_body
    token = resp_body['access_token']
    return token

@pytest.fixture(scope='function', autouse=False)
def random_task_user_1(test_user_1):
    with app.app_context():
        random_task_user_1 = TaskModel.query.filter_by(user_id=test_user_1['id']).order_by(func.random()).limit(1).all()[0]
        return random_task_user_1.__dict__

class TestTasksAPI__SUCCESS:

    def test_get_list_of_tasks(self, token_user_1, test_user_1):
        """
            TEST GET Request to get all Tasks in DB
            belonging to Logged User
        """
        
        response = requests.get('{}/tasks/'.format(ROOT_URL),
            headers={
                'Authorization': 'Bearer {}'.format(token_user_1)
            })
        nbr_of_tasks_in_response = len(response.json())
        assert nbr_of_tasks_in_response > 0
        with app.app_context():
            nbr_of_tasks_in_db = len(TaskModel.query.filter_by(user_id=test_user_1['id']).all())
            assert nbr_of_tasks_in_response == nbr_of_tasks_in_db

    def test_get_specific_task(self, token_user_1, random_task_user_1):
        """
            TEST Get A Specific Task Details from DB belonging to logged user
        """
        with app.app_context():
            response = requests.get(
                '{}/tasks/{}/'.format(ROOT_URL, random_task_user_1['id']),
                headers={'Authorization': 'Bearer {}'.format(token_user_1)}
                )
            resp_body = response.json()
            assert response.status_code == 200, 'Should get a 200 Code Response. Got a %s instead' % response.status_code
            assert resp_body['id'] == random_task_user_1['id'], 'Expecting ID of retrieved Task to be the same as the one requested'
            assert resp_body['title'] == random_task_user_1['title'], 'Expecting title of retrieved Task to be the same as the one in DB'
            assert 'created' in resp_body, 'Expecting created field to show in dump'

    def test_post_new_task(self, token_user_1, test_user_1):
        """
            TEST POST Request to add a new Task in DB
        """
        new_task = { 
            'title': 'New Task Test',
            'comment': 'Comment for new Task',
            'due': datetime(2020,4,22).isoformat(),
            'done': False
        }
        with app.app_context():
            nbr_of_tasks_in_db = len(TaskModel.query.filter_by(user_id=test_user_1['id']).all())
            response = requests.post(
                '{}/tasks/'.format(ROOT_URL),
                headers={'Authorization': 'Bearer {}'.format(token_user_1)},
                json=new_task
                )
            assert response.status_code == 201, 'Should get a 201 Code Response'
            assert nbr_of_tasks_in_db + 1 == len(TaskModel.query.filter_by(user_id=test_user_1['id']).all()) , 'Expecting number of tasks in DB to increase by one'
            assert response.json()['title'] == new_task['title'], 'Expecting title of returned object to match title sent in post request'
            assert response.json()['user_id'] == test_user_1['id'], 'Expecting user_id of returned object to match user_id of logged user'

    def test_patch_task(self, token_user_1, random_task_user_1):
        """
            TEST PATCH Request to update a Task in DB
        """
        with app.app_context():
            new_title = 'Updated Title of Task'
            updated_task = {
                'title' : new_title,
                'comment': 'New Comment for new Task',
                'due': datetime(2020,4,22).isoformat(),
                'done': True
            }
            response = requests.patch (
                '{}/tasks/{}/'.format(ROOT_URL, random_task_user_1['id']),
                headers={'Authorization': 'Bearer {}'.format(token_user_1)},
                json=updated_task )
            assert response.status_code == 200, 'Should get a 200 Code Response'
            updated_task = TaskModel.query.get(random_task_user_1['id']).__dict__
            assert updated_task['title'] == new_title, 'Expected to update the new title in DB'

    def test_delete_task(self, token_user_1, random_task_user_1):
        """
            TEST DELETE Request to delete a Task from DB
        """
        with app.app_context():
            user_id = random_task_user_1['user_id']
            pre_nbr_of_tasks_in_db = len(TaskModel.query.filter_by(user_id=user_id).all())
            response = requests.delete(
                '{}/tasks/{}/'.format(ROOT_URL, random_task_user_1['id']),
                headers={'Authorization': 'Bearer {}'.format(token_user_1)},
                )
            assert response.status_code == 204, 'Should get a 201 Code Response'
            nbr_of_tasks_in_db = len(TaskModel.query.filter_by(user_id=user_id).all())
            assert nbr_of_tasks_in_db  == pre_nbr_of_tasks_in_db - 1, 'Expecting number of tasks in DB to decrease by one'

class TestTasksAPI__FAILURE:

    def test_get_specific_task__not_in_db(self, token_user_1):
        """
            TEST Get A Specific Task Details which doesnt exist in DB
        """
        with app.app_context():
            wrong_id = 123321123
            response = requests.get(
                '{}/tasks/{}/'.format(ROOT_URL, wrong_id),
                headers={'Authorization': 'Bearer {}'.format(token_user_1)}
                )
            assert response.status_code == 404, 'Expecting 404 Response when task id is not in DB'

    def test_post_new_task__invalid_data(self, token_user_1, test_user_1):
        """
            TEST POST Request to add a new Task in DB with invalid data
        """
        new_task = { 
            'title': '' # empty title !
        }
        with app.app_context():
            response = requests.post(
                '{}/tasks/'.format(ROOT_URL),
                headers={'Authorization': 'Bearer {}'.format(token_user_1)},
                json=new_task
                )
            assert response.status_code == 400, 'Should get a 400 Invalid Code Response when providind empty title'
        new_task = { 
            # no title !
        }
        with app.app_context():
            response = requests.post(
                '{}/tasks/'.format(ROOT_URL),
                headers={'Authorization': 'Bearer {}'.format(token_user_1)},
                json=new_task
                )
            assert response.status_code == 400, 'Should get a 400 Invalid Code Response when no title is provided'


    def test_patch_task__not_in_db(self, token_user_1, random_task_user_1):
        """
            TEST PATCH Request to update a Task not in DB ( Wrong Task ID )
        """
        with app.app_context():
            wrong_id = 123321123
            new_title = 'Updated Title of Task'
            response = requests.patch(
                '{}/tasks/{}/'.format(ROOT_URL, wrong_id),
                headers={'Authorization': 'Bearer {}'.format(token_user_1)},
                json={ 'title': new_title })
            assert response.status_code == 404, 'Should get a 404 Code Response when non existing task is provided'

    def test_patch_task__not_belonging_to_logged_user(self, token_user_2, random_task_user_1):
        """
            TEST PATCH Request to update a Task in DB Not belonging to logged user
        """
        with app.app_context():
            new_title = 'Updated Title of Task'
            response = requests.patch(
                '{}/tasks/{}/'.format(ROOT_URL, random_task_user_1['id']),
                headers={'Authorization': 'Bearer {}'.format(token_user_2)},
                json={ 'title': new_title })
            assert response.status_code == 403, 'Should get a 403 Code Response when trying to patch a task not belonging to logged user'

    def test_patch_task__invalid_request(self, token_user_1, random_task_user_1):
        """
            TEST PATCH Request to update a Task with invalid request
        """
        with app.app_context():
            new_title = '' # Empty title
            response = requests.patch(
                '{}/tasks/{}/'.format(ROOT_URL, random_task_user_1['id']),
                headers={'Authorization': 'Bearer {}'.format(token_user_1)},
                json={ 'title': new_title })
            assert response.status_code == 400, 'Should get a 400 Code Response when trying to patch a task with empty title'


    def test_delete_task__not_in_db(self, token_user_1):
        """
            TEST DELETE Request to delete a Task 
            not belonging to current logged user
        """
        wrong_id = 123321123
        response = requests.delete(
            '{}/tasks/{}/'.format(ROOT_URL, wrong_id),
            headers={'Authorization': 'Bearer {}'.format(token_user_1)},
            )
        assert response.status_code == 404, 'Should get a 404 Code Response When trying to delete a task not existing in DB'


    def test_delete_task__not_belonging_to_logged_user(self, token_user_2, random_task_user_1):
        """
            TEST DELETE Request to delete a Task 
            not belonging to current logged user
        """
        response = requests.delete(
            '{}/tasks/{}/'.format(ROOT_URL, random_task_user_1['id']),
            headers={'Authorization': 'Bearer {}'.format(token_user_2)},
            )
        assert response.status_code == 403, 'Should get a 403 Code Response When trying to delete a task not belonging to logged user'
