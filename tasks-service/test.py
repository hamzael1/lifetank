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
            Check Get all Tasks Request
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
            Check Get A Specific Task Details
        """
        with app.app_context():
            random_task = TaskModel.query.all()[0].__dict__
            response = requests.get('{}/tasks/{}/'.format(ROOT_URL, random_task['id']))
            assert response.status_code == 200, 'Should get a 200 Code Response. Got a %s instead' % response.status_code
            assert response.json()['id'] == random_task['id'], 'ID of retrieved Task is different'
            assert response.json()['title'] == random_task['title'], 'title of retrieved Task is different'

