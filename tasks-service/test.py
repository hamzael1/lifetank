import requests
import pytest
from app import app
from model import db, TaskModel

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
                    user_id=user_1_id
                )
            db.session.add(t)
        db.session.commit()
        for i in range(NBR_TASKS_PER_USER):
            t = TaskModel (
                    title='Task Test {}'.format(i+1),
                    user_id=user_2_id
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

class TestTasksAPI:

    def test_get_list_of_tasks(self, test_user_1):
        """
            TEST GET Request to get all Tasks in DB
            belonging to Logged User
        """
        response = requests.post(LOGIN_URL, json={
            'username': test_user_1['username'],
            'password': test_user_1['password'],
        })
        assert response.status_code == 200

        resp_body = response.json()
        assert response.status_code == 200 and 'access_token' in resp_body
        token = resp_body['access_token']
        response = requests.get('{}/tasks/'.format(ROOT_URL),
            headers={
                'Authorization': 'Bearer {}'.format(token)
            })
        nbr_of_tasks_in_response = len(response.json())
        assert nbr_of_tasks_in_response > 0
        with app.app_context():
            nbr_of_tasks_in_db = len(TaskModel.query.filter_by(user_id=test_user_1['id']).all())
            assert nbr_of_tasks_in_response == nbr_of_tasks_in_db
    '''
    def test_get_specific_task(self):
        """
            TEST Get A Specific Task Details from DB
        """
        with app.app_context():
            random_task = TaskModel.query.all()[0].__dict__
            response = requests.get('{}/tasks/{}/'.format(ROOT_URL, random_task['id']))
            assert response.status_code == 200, 'Should get a 200 Code Response. Got a %s instead' % response.status_code
            assert response.json()['id'] == random_task['id'], 'Expecting ID of retrieved Task to be the same as the one requested'
            assert response.json()['title'] == random_task['title'], 'Expecting title of retrieved Task to be the same as the one in DB'

    def test_post_new_task(self):
        """
            TEST POST Request to add a new Task in DB
        """
        with app.app_context():
            nbr_of_tasks_in_db = len(TaskModel.query.all())
            response = requests.post('{}/tasks/'.format(ROOT_URL), json={
                'title': 'New Task Test'
            })
            assert response.status_code == 201, 'Should get a 201 Code Response'
            assert nbr_of_tasks_in_db + 1 == len(TaskModel.query.all()) , 'Expecting number of tasks in DB to increase by one'
            assert response.json()['title'] == 'New Task Test', 'Expecting title of returned object to match title sent in post request'
    
    def test_patch_task(self):
        """
            TEST PATCH Request to update a Task in DB
        """
        with app.app_context():
            random_task = TaskModel.query.all()[0].__dict__
            new_title = 'Updated Title of Task'
            response = requests.patch('{}/tasks/{}/'.format(ROOT_URL, random_task['id']), json={
                'title': new_title
            })
            assert response.status_code == 200, 'Should get a 200 Code Response'
            updated_task = TaskModel.query.get(random_task['id']).__dict__
            assert updated_task['title'] == new_title, 'Expected to update the new title in DB'

    def test_delete_task(self):
        """
            TEST DELETE Request to delete a Task from DB
        """
        with app.app_context():
            nbr_of_tasks_in_db = len(TaskModel.query.all())
            random_task = TaskModel.query.all()[0].__dict__
            response = requests.delete('{}/tasks/{}/'.format(ROOT_URL, random_task['id']))
            assert response.status_code == 204, 'Should get a 201 Code Response'
            assert nbr_of_tasks_in_db - 1 == len(TaskModel.query.all()) , 'Expecting number of tasks in DB to decrease by one'
    '''