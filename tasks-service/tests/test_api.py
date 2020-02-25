import pytest
from sqlalchemy.sql.expression import func
from service_app.model import db, TaskModel

from datetime import datetime
from random import random as rand, randrange, choice

from conftest import NBR_TEST_TASKS_PER_USER, TEST_USERS

ROOT_URL = ''

def test_dummy(app_client):
    response = app_client.get('{}/dummy'.format(ROOT_URL))
    assert response.status_code == 200
    resp_body = response.get_json()
    assert resp_body['message'] == 'Working'


class TestTasksAPI__GetTasks:

    def test_get_user_list_of_tasks(self, app_client, random_user):
        """
            TEST GET Request to get all Tasks in DB
            belonging to a specified User
        """
        response = app_client.get('{}/?owner={}'.format(ROOT_URL, random_user['id']),
            headers={})
        assert response.status_code == 200

        tasks = response.get_json()
        nbr_of_tasks_in_response = len(tasks)    
        assert nbr_of_tasks_in_response ==  NBR_TEST_TASKS_PER_USER
        assert choice(tasks)['owner_user_id'] == random_user['id']

    def test_get_specific_task(self, app_client, random_task):
        """
            TEST Get A Specific Task Details from DB belonging to logged user
        """
        response = app_client.get(
            '{}/{}'.format(ROOT_URL, random_task['id']),
            headers={}
            )
        resp_body = response.get_json()
        assert response.status_code == 200, 'Should get a 200 Code Response. Got a %s instead' % response.status_code
        assert resp_body['id'] == random_task['id'], 'Expecting ID of retrieved Task to be the same as the one requested'
        assert resp_body['title'] == random_task['title'], 'Expecting title of retrieved Task to be the same as the one in DB'
        assert 'created' in resp_body, 'Expecting created field to show in dump'

    def test_get_specific_task__not_in_db(self, app_client, wrong_task_id):
        """
            TEST Get A Specific Task Details which doesnt exist in DB
        """
        response = app_client.get(
            '{}/{}'.format(ROOT_URL, wrong_task_id),
            headers={}
            )
        assert response.status_code == 404, 'Expecting 404 Response when task id is not in DB'



INVALID_TASKS = [
        ({ 'owner_user_id': choice(TEST_USERS)['id'], 'title' : '', 'comment': 'comment', 'due': datetime(2020,4,22).isoformat(), 'done': True }, 'providing empty title'),
        ({ 'owner_user_id': choice(TEST_USERS)['id'], 'title' : 'title', 'comment': 'comment',  'done': True }, 'no Due field is provided'),
        ({ 'owner_user_id': None, 'title' : 'title', 'comment': 'comment', 'due': datetime(2020,4,22).isoformat(), 'done': True }, 'no owner_user_id is provided'),
]

class TestTasksAPI__PostTask:

    def test_post_new_task__success(self, app, app_client, random_user):
        """
            TEST POST Request to add a new Task in DB
        """
        new_task = { 
            'owner_user_id': random_user['id'],
            'title': 'New Task Test',
            'comment': 'Comment for new Task',
            'due': datetime(2020,4,22).isoformat(),
            'done': False
        }
        with app.app_context():
            nbr_of_tasks_in_db = len(TaskModel.query.filter_by(owner_user_id=random_user['id']).all())
            response = app_client.post(
                '{}/'.format(ROOT_URL),
                headers={},
                json=new_task
                )
            assert response.status_code == 201, 'Should get a 201 Code Response'
            assert nbr_of_tasks_in_db + 1 == len(TaskModel.query.filter_by(owner_user_id=random_user['id']).all()) , 'Expecting number of tasks in DB to increase by one'
            resp_body = response.get_json()
            assert resp_body['title'] == new_task['title'], 'Expecting title of returned object to match title sent in post request'
            assert resp_body['owner_user_id'] == random_user['id'], 'Expecting user_id of returned object to match user_id of logged user'

    @pytest.mark.parametrize('invalid_new_task, expected_str', INVALID_TASKS)
    def test_post_new_task__invalid_data(self, app_client, invalid_new_task, expected_str):
        """
            TEST POST Request to add a new Task in DB with invalid data
        """
        response = app_client.post(
            '{}/'.format(ROOT_URL),
            headers={},
            json=invalid_new_task
            )
        assert response.status_code == 400, 'Expecting to get a 400 Invalid Request when {}'.format(expected_str)



class TestTasksAPI__UpdateTask:
    
    def test_patch_task__success(self, app, app_client, random_user, random_task):
        """
            TEST PATCH Request to update a Task in DB
        """
        with app.app_context():
            new_title = 'Updated Title of Task'
            updated_task = {
                'owner_user_id': random_user['id'],
                'title' : new_title,
                'comment': 'New Comment for new Task',
                'due': datetime(2020,4,22).isoformat(),
                'done': True
            }
            response = app_client.patch (
                '{}/{}'.format(ROOT_URL, random_task['id']),
                headers={},
                json=updated_task )
            assert response.status_code == 200, 'Should get a 200 Code Response'
            updated_task = TaskModel.query.get(random_task['id']).__dict__
            assert updated_task['title'] == new_title, 'Expected to update the new title in DB'

    def test_patch_task__not_in_db(self, app_client, wrong_task_id, random_user):
        """
            TEST PATCH Request to update a Task not in DB ( Wrong Task ID )
        """
        updated_task = {
            'owner_user_id': random_user['id'],
            'title' : 'new_title',
            'comment': 'New Comment for new Task',
            'due': datetime(2020,4,22).isoformat(),
            'done': True
        }
        response = app_client.patch(
            '{}/{}'.format(ROOT_URL, wrong_task_id),
            headers={},
            json=updated_task)
        assert response.status_code == 404, 'Should get a 404 Code Response when non existing task is provided'

    @pytest.mark.parametrize('invalid_patch_task, expected_str', INVALID_TASKS)
    def test_patch_task__invalid_request(self, app_client, random_task, invalid_patch_task, expected_str):
        """
            TEST PATCH Request to update a Task with invalid request
        """
        response = app_client.patch(
            '{}/{}'.format(ROOT_URL, random_task['id']),
            headers={},
            json=invalid_patch_task)
        assert response.status_code == 400, 'Should get a 400 Code Response when {}'.format(expected_str)


class TestTasksAPI__DeleteTask:

    def test_delete_task__success(self, app, app_client, random_task):
        """
            TEST DELETE Request to delete a Task from DB
        """
        with app.app_context():
            pre_nbr_of_tasks_in_db = len(TaskModel.query.all())
            response = app_client.delete(
                '{}/{}'.format(ROOT_URL, random_task['id']),
                headers={},
                )
            assert response.status_code == 204, 'Should get a 201 Code Response'
            nbr_of_tasks_in_db = len(TaskModel.query.all())
            assert nbr_of_tasks_in_db  == pre_nbr_of_tasks_in_db - 1, 'Expecting number of tasks in DB to decrease by one'

    def test_delete_task__not_in_db(self, app_client, wrong_task_id):
        """
            TEST DELETE Request to delete a Task 
            not belonging to current logged user
        """
        response = app_client.delete(
            '{}/{}'.format(ROOT_URL, wrong_task_id),
            headers={},
            )
        assert response.status_code == 404, 'Should get a 404 Code Response When trying to delete a task not existing in DB'
