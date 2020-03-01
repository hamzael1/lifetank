from click import echo, option, group, argument
import requests
import os
from datetime import datetime, timedelta

from .settings import HOST, PORT



HEADERS = {'Authorization': 'Bearer {}'.format(os.environ.get('LIFETANK_ATOKEN'))}
EXPENSES_FETCH_LIST_URL = 'http://{}:{}/expenses'.format(HOST, PORT)
EXPENSES_ADD_URL = 'http://{}:{}/expenses'.format(HOST, PORT)
EXPENSES_EDIT_URL = 'http://{}:{}/expenses/'.format(HOST, PORT)
EXPENSES_DELETE_URL = 'http://{}:{}/expenses/'.format(HOST, PORT)
DEFAULT_DATE = datetime.today().strftime('%Y-%m-%d')

@group()
def expense():
    echo('Expenses ...')

def print_expense(d, details=False):
    echo('\n - [ {} ] {} ~{}~ ({})'.format(
        d['id'],
        d['title'],
        d['amount'],
        datetime.strptime(d['date'].split('T')[0], '%Y-%m-%d').strftime('%Y-%m-%d'))
        )

@expense.command()
def fetch():
    echo('Fetching Expenses')
    resp = requests.get(EXPENSES_FETCH_LIST_URL, json={}, headers=HEADERS)
    if resp.status_code == 200:
        expenses = resp.json()
        echo('\nExpenses: {}'.format(len(expenses)))
        for t in expenses:
            print_expense(t, details=False)
    else:
        echo('Unexpected Response from server (Code {})'.format(resp.status_code))


@expense.command()
@option('--task_id', prompt=True, default=0, help='Task of Expense')
@option('--title', prompt=True, help='Title of expense')
@option('--comment', prompt=True, default='', help='Comment of expense')
@option('--date', prompt=True, default=DEFAULT_DATE, help='Date of Expense')
@option('--amount', prompt=True, default=0, help='Amount of expense')
@option('--category', prompt=True, default='OTHER', help='Expense category')
def add(task_id, title, comment, date, amount, category):
    hidden = False
    try:
        date = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        echo('Error Converting Due Date. Please respect the format YYYY-MM-DD')
    payload = {
        'task_id': task_id,
        'title': title,
        'comment': comment,
        'date': date.isoformat(),
        'amount': amount,
        'category': category,
    }
    resp = requests.post(EXPENSES_ADD_URL, json=payload, headers=HEADERS)
    if resp.status_code == 201:
        echo('Expense Added successfully')
    elif resp.status_code == 400:
        errors = resp.json()['errors']
        for f,err in errors.items():
            echo('{} {}'.format(f, err))
    else:
        echo('Unexpected Response from server (Code {})'.format(resp.status_code))

@expense.command()
@argument('expense_id', nargs=1)
@option('--task_id', prompt=True, default=0, help='Task of Expense')
@option('--title', prompt=True, help='Title of expense')
@option('--comment', prompt=True, default='', help='Comment of expense')
@option('--date', prompt=True, default=DEFAULT_DATE, help='Date of Expense')
@option('--amount', prompt=True, default=0, help='Amount of expense')
@option('--category', prompt=True, default='OTHER', help='Expense category')
def edit(expense_id, task_id, title, comment, date, amount, category):
    try:
        date = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        echo('Error Converting Due Date. Please respect the format YYYY-MM-DD')
    payload = {
        'task_id': task_id,
        'title': title,
        'comment': comment,
        'date': date.isoformat(),
        'amount': amount,
        'category': category,
    }
    resp = requests.patch('{}{}'.format(EXPENSES_EDIT_URL, expense_id), json=payload, headers=HEADERS)
    if resp.status_code == 200:
        echo('Expense Edited successfully')
    elif resp.status_code == 400:
        errors = resp.json()['errors']
        for f,err in errors.items():
            echo('{} {}'.format(f, err))
    else:
        echo('Unexpected Response from server (Code {})'.format(resp.status_code))

@expense.command()
@argument('expense_id', nargs=1)
def delete(expense_id):
    resp = requests.delete('{}{}'.format(EXPENSES_DELETE_URL, expense_id), json={}, headers=HEADERS )
    if resp.status_code == 204:
        echo('Expense Deleted successfully')
    elif resp.status_code == 404:
        echo('Expense or endpoint not found')
    else:
        echo('Unexpected Response from server (Code {})'.format(resp.status_code))
