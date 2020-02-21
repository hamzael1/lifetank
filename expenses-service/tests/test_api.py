import pytest
from sqlalchemy.sql.expression import func
from flask_jwt_extended import decode_token
from service_app.model import db, ExpenseModel

from datetime import datetime, timedelta
from random import random as rand, randrange, choice, choices

from conftest import NBR_TEST_EXPENSES_PER_TASK, TEST_TASKS_IDS, TODAY

ROOT_URL = '/expenses'

def test_dummy(app_client):
    response = app_client.get('{}/dummy'.format(ROOT_URL))
    assert response.status_code == 200
    resp_body = response.get_json()
    assert resp_body['message'] == 'Working'

class TestExpensesAPI__GetExpenses:

    def test_get_list_of_expenses(self, app_client):
        """
            TEST GET Request to get Expenses of task ids specified in json body
        """
        nbr_tasks = randrange(1, len(TEST_TASKS_IDS))
        task_ids = list(set(choices(TEST_TASKS_IDS, k=nbr_tasks)))
        nbr_tasks = len(task_ids)
        response = app_client.get(
            '{}'.format(ROOT_URL),
            json={'task_ids': task_ids},
        )
        assert response.status_code == 200

        nbr_of_expenses_in_response = len(response.get_json())    
        assert nbr_of_expenses_in_response ==  NBR_TEST_EXPENSES_PER_TASK*nbr_tasks

    def test_get_specific_expense(self, app_client, random_expense):
        """
            TEST Get A Specific Expense Details from DB belonging to logged user
        """
        response = app_client.get(
            '{}/{}/'.format(ROOT_URL, random_expense['id']),
            )
        resp_body = response.get_json()
        assert response.status_code == 200, 'Should get a 200 Code Response. Got a %s instead' % response.status_code
        assert resp_body['id'] == random_expense['id'], 'Expecting ID of retrieved Expense to be the same as the one requested'
        assert resp_body['title'] == random_expense['title'], 'Expecting title of retrieved Expense to be the same as the one in DB'

    def test_get_specific_expense__not_in_db(self, app_client, wrong_expense_id):
        """
            TEST Get A Specific Expense Details which doesnt exist in DB
        """
        response = app_client.get(
            '{}/{}/'.format(ROOT_URL, wrong_expense_id),
            )
        assert response.status_code == 404, 'Expecting 404 Response when expense id is not in DB'


INVALID_EXPENSES = [
    ( { 'title': '', 'comment': 'comment', 'category': choice(ExpenseModel.EXPENSE_CATEGORIES), 'amount': randrange(1,1000), 'date':TODAY + timedelta(days=randrange(1,100)), 'task_id': choice(TEST_TASKS_IDS) }, 'no title is provided' ),
    ( { 'title': 'title', 'comment': 'comment', 'category': '', 'amount': randrange(1,1000), 'date':TODAY + timedelta(days=randrange(1,100)), 'task_id': choice(TEST_TASKS_IDS) }, 'category is empty' ),
    ( { 'title': 'title', 'comment': 'comment', 'category': choice(ExpenseModel.EXPENSE_CATEGORIES), 'amount': 0, 'date':TODAY + timedelta(days=randrange(1,100)), 'task_id': choice(TEST_TASKS_IDS) }, 'amount is zero' ),
    ( { 'title': 'title', 'comment': 'comment', 'category': choice(ExpenseModel.EXPENSE_CATEGORIES), 'amount': 0, 'task_id': choice(TEST_TASKS_IDS) }, 'no date is provided' ),
]

class TestExpensesAPI__PostExpense:

    def test_post_new_expense__success(self, app, app_client):
        """
            TEST POST Request to add a new Expense in DB
        """
        new_expense = {
                'title': 'title for expense',
                'comment': 'comment for expense',
                'category': choice(ExpenseModel.EXPENSE_CATEGORIES),
                'amount': randrange(1,1000),
                'date': (TODAY + timedelta(days=randrange(1,100))).isoformat(),
                'task_id': choice(TEST_TASKS_IDS)
            }
        with app.app_context():
            nbr_of_expenses_in_db = len(ExpenseModel.query.all())
            response = app_client.post(
                '{}'.format(ROOT_URL),
                json=new_expense
                )
            print(response.get_json())
            assert response.status_code == 201, 'Should get a 201 Code Response'
            assert nbr_of_expenses_in_db + 1 == len(ExpenseModel.query.all()) , 'Expecting number of expenses in DB to increase by one'
            resp_body = response.get_json()
            assert resp_body['title'] == new_expense['title'], 'Expecting title of returned object to match title sent in post request'

    @pytest.mark.parametrize('invalid_new_expense, expected_str', INVALID_EXPENSES)
    def test_post_new_expense__invalid_data(self, app_client, invalid_new_expense, expected_str):
        """
            TEST POST Request to add a new Expense in DB with invalid data
        """
        response = app_client.post(
            '{}'.format(ROOT_URL),
            json=invalid_new_expense
            )
        assert response.status_code == 400, 'Expecting to get a 400 Invalid Request when {}'.format(expected_str)


class TestExpensesAPI__UpdateExpense:
    
    def test_patch_expense__success(self, app, app_client, random_expense):
        """
            TEST PATCH Request to update a Expense in DB
        """
        with app.app_context():
            new_title = 'Updated Title of Expense'
            updated_expense = {
                'title': new_title,
                'comment': 'new comment for expense',
                'category': choice(ExpenseModel.EXPENSE_CATEGORIES),
                'amount': randrange(1,1000),
                'date': (TODAY + timedelta(days=randrange(1,100))).isoformat(),
                'task_id': choice(TEST_TASKS_IDS)
            }
            response = app_client.patch (
                '{}/{}/'.format(ROOT_URL, random_expense['id']),
                json=updated_expense )
            assert response.status_code == 200, 'Should get a 200 Code Response'
            updated_expense = ExpenseModel.query.get(random_expense['id']).__dict__
            assert updated_expense['title'] == new_title, 'Expected to update the new title in DB'

    def test_patch_expense__not_in_db(self, app_client, wrong_expense_id):
        """
            TEST PATCH Request to update a Expense not in DB ( Wrong Expense ID )
        """
        updated_expense =  {
                'title': 'new title',
                'comment': 'new comment for expense',
                'category': choice(ExpenseModel.EXPENSE_CATEGORIES),
                'amount': randrange(1,1000),
                'date': (TODAY + timedelta(days=randrange(1,100))).isoformat(),
                'task_id': choice(TEST_TASKS_IDS)
            }
        response = app_client.patch(
            '{}/{}/'.format(ROOT_URL, wrong_expense_id),
            json=updated_expense)
        assert response.status_code == 404, 'Should get a 404 Code Response when non existing expense is provided'

    @pytest.mark.parametrize('invalid_patch_expense, expected_str', INVALID_EXPENSES)
    def test_patch_expense__invalid_request(self, app_client, random_expense, invalid_patch_expense, expected_str):
        """
            TEST PATCH Request to update a Expense with invalid request
        """
        response = app_client.patch(
            '{}/{}/'.format(ROOT_URL, random_expense['id']),
            json=invalid_patch_expense)
        assert response.status_code == 400, 'Should get a 400 Code Response when {}'.format(expected_str)

class TestExpensesAPI__DeleteExpense:

    def test_delete_expense__success(self, app, app_client, random_expense):
        """
            TEST DELETE Request to delete a Expense from DB
        """
        with app.app_context():
            pre_nbr_of_expenses_in_db = len(ExpenseModel.query.all())
            response = app_client.delete(
                '{}/{}/'.format(ROOT_URL, random_expense['id']),
                )
            assert response.status_code == 204, 'Should get a 201 Code Response'
            nbr_of_expenses_in_db = len(ExpenseModel.query.all())
            assert nbr_of_expenses_in_db  == pre_nbr_of_expenses_in_db - 1, 'Expecting number of expenses in DB to decrease by one'

    def test_delete_expense__not_in_db(self, app_client, wrong_expense_id):
        """
            TEST DELETE Request to delete a Expense 
            not belonging to current logged user
        """
        response = app_client.delete(
            '{}/{}/'.format(ROOT_URL, wrong_expense_id),
            )
        assert response.status_code == 404, 'Should get a 404 Code Response When trying to delete a expense not existing in DB'