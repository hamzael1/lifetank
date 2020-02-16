import requests
import pytest
from app import app
from model import db, TaskModel

ROOT_URL='http://localhost:5000'

def populate_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        for i in range(10):
            t = TaskModel(title='Task Test %s' % i)
            db.session.add(t)
        db.session.commit()

@pytest.fixture(scope='module', autouse=True)
def init_db_for_test_session(request):
    db.init_app(app)
    populate_db()
    def fin():
        with app.app_context():
            db.drop_all()
    request.addfinalizer(fin)

class TestTasksAPI:

    def test_get_list_of_tasks(self):
        """
            TEST GET Request to get all Tasks in DB
        """
        response = requests.get('{}/tasks/'.format(ROOT_URL))
        assert response.status_code == 200
        nbr_of_tasks_in_response = len(response.json())
        assert nbr_of_tasks_in_response > 0
        with app.app_context():
            nbr_of_tasks_in_db = len(TaskModel.query.all())
            assert nbr_of_tasks_in_db == nbr_of_tasks_in_response

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
