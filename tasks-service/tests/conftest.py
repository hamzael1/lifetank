import pytest
from  sqlalchemy.sql.expression import func

from service_app.model import  populate_db, TaskModel
from service_app import create_app

from random import choice, randrange


NBR_TEST_TASKS_PER_USER = 14

TEST_USERS = [
    { 'id': 1000, 'username': 'test_user_1' },
    { 'id': 1001, 'username': 'test_user_2' }
]

@pytest.fixture(scope='module', autouse=False)
def app():
    app = create_app(testing=True)
    populate_db(app, user_ids=[u['id'] for u in TEST_USERS], nbr_tasks_per_user=NBR_TEST_TASKS_PER_USER)
    return app

@pytest.fixture(scope='module', autouse=False)
def app_client(app):
    return app.test_client()


@pytest.fixture(scope='function', autouse=False)
def random_user():
    return choice(TEST_USERS)

@pytest.fixture(scope='function', autouse=False)
def random_task(app):
    with app.app_context():
        return choice(TaskModel.query.all()).__dict__

@pytest.fixture(scope='function', autouse=False)
def wrong_task_id(app): # Returns ID of task not existing in DB
    with app.app_context():
        id = randrange(randrange(90, 99), randrange(400, 600)) * randrange(randrange(90, 99), randrange(400, 600))
        while TaskModel.query.get(id) != None:
            id += randrange(100,600)
        return id