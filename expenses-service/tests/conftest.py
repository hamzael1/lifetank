import pytest
from  sqlalchemy.sql.expression import func

from service_app.model import  populate_db, ExpenseModel
from service_app import create_app

from random import choice, randrange

from datetime import datetime, timedelta

NBR_TEST_EXPENSES_PER_TASK = 14
NBR_TASKS = 10
TEST_TASKS_IDS = [ (i+1) for i in range(NBR_TASKS) ]

TODAY = datetime.today()
TEST_EXPENSES = []
cnt = 1
for tid in TEST_TASKS_IDS:
        TEST_EXPENSES.extend(
        [ {
                'id': cnt, 
                'title': 'title for expense {}'.format(cnt),
                'comment': 'comment for expense {}'.format(cnt),
                'category': choice(ExpenseModel.EXPENSE_CATEGORIES),
                'amount': randrange(1,1000),
                'date':TODAY + timedelta(days=randrange(1,100)),
                'task_id': tid
            } for i in range(NBR_TEST_EXPENSES_PER_TASK) ] 
        )
        cnt += 1

@pytest.fixture(scope='module', autouse=False)
def app():
    app = create_app(testing=True)
    populate_db(app, expenses_to_add=TEST_EXPENSES)
    return app

@pytest.fixture(scope='module', autouse=False)
def app_client(app):
    return app.test_client()


@pytest.fixture(scope='function', autouse=False)
def random_expense(app):
    with app.app_context():
        return choice(ExpenseModel.query.all()).__dict__

@pytest.fixture(scope='function', autouse=False)
def wrong_expense_id(app):
    with app.app_context():
        id = randrange(randrange(90, 99), randrange(400, 600)) * randrange(randrange(90, 99), randrange(400, 600))
        while ExpenseModel.query.get(id) != None:
            id += randrange(100,600)
        return id