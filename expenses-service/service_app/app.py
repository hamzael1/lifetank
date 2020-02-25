import os
import sys

from flask import Flask

from .model import init_db, populate_db
from .routes import init_routes


def create_app(testing=False):
    app = Flask(__name__, instance_relative_config=True)
    app.config['TESTING'] = testing
    print('Creating Flask App ({}{})...'.format(app.config['ENV'], ' - Testing' if testing else '')) 
    # Get Config depending on current ENV 
    # ( set FLASK_ENV environment variable to "development" or "production" ;
    # default is "production" )
    app.config.from_object('service_app.config.{}'.format(app.config['ENV']))
    
    # Init SQLAlchemy DB.
    init_db(app)
    # Populate DB with some dummy users if in dev environment
    if app.config['ENV'] == 'development' and not testing:
        from datetime import datetime, timedelta
        from random import randrange, choice
        from .model import ExpenseModel
        NBR_TEST_EXPENSES_PER_TASK = 14
        NBR_TEST_TASKS = 10
        NBR_TEST_USERS = 5
        TEST_TASKS_IDS = [ randrange(1,1000) for _ in range(NBR_TEST_TASKS) ]
        TEST_USER_IDS = [ randrange(1,1000) for _ in range(NBR_TEST_USERS) ]

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
                        'owner_user_id': choice(TEST_USER_IDS), 
                        'task_id': tid
                    } for i in range(NBR_TEST_EXPENSES_PER_TASK) ] 
                )
                cnt += 1

        populate_db(app, expenses_to_add=TEST_EXPENSES)

    
    # Init Routes
    init_routes(app)

    return app


