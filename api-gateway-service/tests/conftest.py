
import pytest
from  sqlalchemy.sql.expression import func

from service_app.model import  populate_db
from service_app import create_app

import random


NBR_TEST_USERS = 3
TEST_USERS = [
    {
        'id': 1000+i,
        'username': 'test_user_{}'.format(i+1),
        'password': 'passpass'
    } for i in range(NBR_TEST_USERS)
]

@pytest.fixture(scope='module', autouse=False)
def app():
    app = create_app(testing=True)
    populate_db(app, TEST_USERS)
    return app

@pytest.fixture(scope='module', autouse=False)
def app_client(app):
    return app.test_client()

@pytest.fixture(scope='function', autouse=False)
def random_test_user(app):
    return random.choice(TEST_USERS)

