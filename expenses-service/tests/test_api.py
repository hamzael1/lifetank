import pytest
from sqlalchemy.sql.expression import func
from service_app.model import db, ExpenseModel

from datetime import datetime, timedelta
from random import random as rand, randrange, choice, choices

from conftest import NBR_TEST_EXPENSES_PER_TASK, TEST_USER_IDS, TEST_TASKS_IDS, TODAY

ROOT_URL = ''

def test_dummy(app_client):
    response = app_client.get('{}/dummy'.format(ROOT_URL))
    assert response.status_code == 200
    resp_body = response.get_json()
    assert resp_body['message'] == 'Working'

class TestExpensesAPI__GetExpenses:

    def test_get_list_of_expenses_by_task_id__success(self, app, app_client, random_task_id):
        """
            TEST GET Request to get Expenses of a specfic task_id specified in URL param
        """
        response = app_client.get(
            '{}/?task_id={}'.format(ROOT_URL, random_task_id)
        )
        assert response.status_code == 200
        nbr_of_expenses_in_response = len(response.get_json()) 
        with app.app_context():
            nbr_of_expenses_of_user_in_db = ExpenseModel.query.filter_by(task_id=random_task_id).count()
            assert nbr_of_expenses_in_response ==  nbr_of_expenses_of_user_in_db

    def test_get_list_of_expenses_by_owner__success(self, app, app_client, random_user_id):
        """
            TEST GET Request to get Expenses of a specfic user specified in URL param
        """
        response = app_client.get(
            '{}/?owner={}'.format(ROOT_URL, random_user_id)
        )
        assert response.status_code == 200
        nbr_of_expenses_in_response = len(response.get_json())
        with app.app_context():
            nbr_of_expenses_of_user_in_db = ExpenseModel.query.filter_by(owner_user_id=random_user_id).count()
            assert nbr_of_expenses_in_response ==  nbr_of_expenses_of_user_in_db


    def test_get_specific_expense(self, app_client, random_expense):
        """
            TEST Get A Specific Expense Details from DB belonging to logged user
        """
        response = app_client.get(
            '{}/{}'.format(ROOT_URL, random_expense['id']),
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
            '{}/{}'.format(ROOT_URL, wrong_expense_id),
            )
        assert response.status_code == 404, 'Expecting 404 Response when expense id is not in DB'



INVALID_EXPENSES = [
    ( { 'owner_user_id': choice(TEST_USER_IDS), 'title': '', 'comment': 'comment', 'category': choice(ExpenseModel.EXPENSE_CATEGORIES), 'amount': randrange(1,1000), 'date':TODAY + timedelta(days=randrange(1,100)), 'task_id': choice(TEST_TASKS_IDS) }, 'no title is provided' ),
    ( { 'owner_user_id': choice(TEST_USER_IDS), 'title': 'title', 'comment': 'comment', 'category': '', 'amount': randrange(1,1000), 'date':TODAY + timedelta(days=randrange(1,100)), 'task_id': choice(TEST_TASKS_IDS) }, 'category is empty' ),
    ( { 'owner_user_id': choice(TEST_USER_IDS), 'title': 'title', 'comment': 'comment', 'category': choice(ExpenseModel.EXPENSE_CATEGORIES), 'amount': 0, 'date':TODAY + timedelta(days=randrange(1,100)), 'task_id': choice(TEST_TASKS_IDS) }, 'amount is zero' ),
    ( { 'owner_user_id': choice(TEST_USER_IDS), 'title': 'title', 'comment': 'comment', 'category': choice(ExpenseModel.EXPENSE_CATEGORIES), 'amount': 0, 'task_id': choice(TEST_TASKS_IDS) }, 'no date is provided' ),
    ( { 'owner_user_id': 0, 'title': 'tltle', 'comment': 'comment', 'category': choice(ExpenseModel.EXPENSE_CATEGORIES), 'amount': randrange(1,1000), 'date':TODAY + timedelta(days=randrange(1,100)), 'task_id': choice(TEST_TASKS_IDS) }, 'no owner user id is provided' ),
]
VALID_EXPENSES = [
                ({ # all fields provided
                'title': 'title for new expense',
                'comment': 'comment for expense',
                'category': choice(ExpenseModel.EXPENSE_CATEGORIES),
                'amount': randrange(1,1000),
                'task_id': choice(TEST_TASKS_IDS),
                'date': (TODAY + timedelta(days=randrange(1,100))).isoformat(),
                }, 'Expected to allow writing expense with all fields provided'),
                ({ # no comment provided
                'title': 'title for new expense',
                'category': choice(ExpenseModel.EXPENSE_CATEGORIES),
                'amount': randrange(1,1000),
                'task_id': choice(TEST_TASKS_IDS),
                'date': (TODAY + timedelta(days=randrange(1,100))).isoformat(),
                }, 'Expected to allow writing expense with no comment provided'),
                ({ # no task_id provided
                'title': 'title for new expense',
                'comment': 'comment for expense',
                'category': choice(ExpenseModel.EXPENSE_CATEGORIES),
                'amount': randrange(1,1000),
                'date': (TODAY + timedelta(days=randrange(1,100))).isoformat(),
                }, 'Expected to allow writing expense with no task_id provided')
    ]

class TestExpensesAPI__PostExpense:

    @pytest.mark.parametrize('new_expense, expected_str', VALID_EXPENSES)
    def test_post_new_expense__success(self, app, app_client, random_task_id, random_user_id, new_expense,  expected_str):
        """
            TEST POST Request to add a new Expense in DB
        """

        with app.app_context():
            new_expense['owner_user_id'] = random_user_id
            nbr_of_expenses_in_db_pre = ExpenseModel.query.count()
            response = app_client.post(
                    '{}/'.format(ROOT_URL),
                    json=new_expense
            )
            print(response.get_json())
            assert response.status_code == 201, 'Should get a 201 Code Response'
            assert nbr_of_expenses_in_db_pre + 1 == ExpenseModel.query.count() , 'Expecting number of expenses in DB to increase by one'
            resp_body = response.get_json()
            assert resp_body['title'] == new_expense['title'], 'Expecting title of returned object to match title sent in post request'

    @pytest.mark.parametrize('invalid_new_expense, expected_str', INVALID_EXPENSES)
    def test_post_new_expense__invalid_data(self, app_client, invalid_new_expense, expected_str):
        """
            TEST POST Request to add a new Expense in DB with invalid data
        """
        response = app_client.post(
            '{}/'.format(ROOT_URL),
            json=invalid_new_expense
            )
        assert response.status_code == 400, 'Expecting to get a 400 Invalid Request when {}'.format(expected_str)


class TestExpensesAPI__UpdateExpense:
    
    @pytest.mark.parametrize('updated_expense, expected_str', VALID_EXPENSES)
    def test_patch_expense__success(self, app, app_client, random_expense, updated_expense, expected_str,random_task_id, random_user_id):
        """
            TEST PATCH Request to update a Expense in DB
        """
        with app.app_context():
            new_title = 'Updated Title of Expense'
            updated_expense['title'] = new_title
            response = app_client.patch (
                '{}/{}'.format(ROOT_URL, random_expense['id']),
                json=updated_expense )
            assert response.status_code == 200, 'Should get a 200 Code Response'
            updated_expense = ExpenseModel.query.get(random_expense['id']).__dict__
            assert updated_expense['title'] == new_title, 'Expected to update the new title in DB'

    def test_patch_expense__not_in_db(self, app_client, wrong_expense_id, random_task_id, random_user_id):
        """
            TEST PATCH Request to update a Expense not in DB ( Wrong Expense ID )
        """
        updated_expense =  {
                'title': 'new title',
                'comment': 'new comment for expense',
                'category': choice(ExpenseModel.EXPENSE_CATEGORIES),
                'amount': randrange(1,1000),
                'date': (TODAY + timedelta(days=randrange(1,100))).isoformat(),
                'owner_user_id': random_user_id,
                'task_id': random_task_id
            }
        response = app_client.patch(
            '{}/{}'.format(ROOT_URL, wrong_expense_id),
            json=updated_expense)
        assert response.status_code == 404, 'Should get a 404 Code Response when non existing expense is provided'

    @pytest.mark.parametrize('invalid_patch_expense, expected_str', INVALID_EXPENSES)
    def test_patch_expense__invalid_request(self, app_client, random_expense, invalid_patch_expense, expected_str):
        """
            TEST PATCH Request to update a Expense with invalid request
        """
        response = app_client.patch(
            '{}/{}'.format(ROOT_URL, random_expense['id']),
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
                '{}/{}'.format(ROOT_URL, random_expense['id']),
                )
            assert response.status_code == 204, 'Should get a 201 Code Response'
            nbr_of_expenses_in_db = ExpenseModel.query.count()
            assert nbr_of_expenses_in_db  == pre_nbr_of_expenses_in_db - 1, 'Expecting number of expenses in DB to decrease by one'

    def test_delete_expense__not_in_db(self, app_client, wrong_expense_id):
        """
            TEST DELETE Request to delete a Expense 
            not belonging to current logged user
        """
        response = app_client.delete(
            '{}/{}'.format(ROOT_URL, wrong_expense_id),
            )
        assert response.status_code == 404, 'Should get a 404 Code Response When trying to delete a expense not existing in DB'
    