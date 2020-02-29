from click import echo, option
import requests
import os
from datetime import datetime, timedelta

HEADERS = {'Authorization': 'Bearer {}'.format(os.environ.get('LIFETANK_ATOKEN'))}
TASKS_FETCH_LIST_URL = 'http://127.0.0.1:8000/tasks'
TASKS_ADD_URL = 'http://127.0.0.1:8000/tasks'
TASKS_EDIT_URL = 'http://127.0.0.1:8000/tasks/'
TASKS_DELETE_URL = 'http://127.0.0.1:8000/tasks/'
DEFAULT_DUE_DATE = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')

def task():
    echo('Tasks ...')

def print_task(d, details=False):
    echo('\n - [ {} ] {} ({}) (due: {})'.format(
        d['id'],
        d['title'],
        'Done' if d['done'] else 'Not Done',
        datetime.strptime(d['due'].split('T')[0], '%Y-%m-%d').strftime('%Y-%m-%d'))
        )

def fetch():
    echo('Fetching Tasks')
    resp = requests.get(TASKS_FETCH_LIST_URL, json={}, headers=HEADERS)
    if resp.status_code == 200:
        tasks = resp.json()
        echo('\nTasks: {}'.format(len(tasks)))
        for t in tasks:
            print_task(t, details=False)
    else:
        echo('Unexpected Response from server (Code {})'.format(resp.status_code))


@option('--title', prompt=True, help='Title of task')
@option('--comment', prompt=True, default='', help='Comment of task')
@option('--due', prompt=True, default=DEFAULT_DUE_DATE, help='Due Date of Task')
@option('--done', prompt=True, default='no', help='Task Done ?')
def add(title, comment, due, done):
    try:
        due = datetime.strptime(due, '%Y-%m-%d')
    except ValueError:
        echo('Error Converting Due Date. Please respect the format YYYY-MM-DD')
    payload = {
        'title': title,
        'comment': comment,
        'due': due.isoformat(),
        'done': done == 'yes'
    }
    resp = requests.post(TASKS_ADD_URL, json=payload, headers=HEADERS)
    if resp.status_code == 201:
        echo('Task Added successfully')
    elif resp.status_code == 400:
        errors = resp.json()['errors']
        for f,err in errors.items():
            echo('{} {}'.format(f, err))
    else:
        echo('Unexpected Response from server (Code {})'.format(resp.status_code))

@option('--task_id', prompt=True, help='ID of task to delete')
@option('--title', prompt=True, help='Title of task')
@option('--comment', prompt=True, default='', help='Comment of task')
@option('--due', prompt=True, default=DEFAULT_DUE_DATE, help='Due Date of Task')
@option('--done', prompt=True, default='no', help='Task Done ?')
def edit(task_id, title, comment, due, done):
    try:
        due = datetime.strptime(due, '%Y-%m-%d')
    except ValueError:
        echo('Error Converting Due Date. Please respect the format YYYY-MM-DD')
    payload = {
        'title': title,
        'comment': comment,
        'due': due.isoformat(),
        'done': done == 'yes'
    }
    resp = requests.patch('{}{}'.format(TASKS_EDIT_URL, task_id), json=payload, headers=HEADERS)
    if resp.status_code == 200:
        echo('Task Edited successfully')
    elif resp.status_code == 400:
        errors = resp.json()['errors']
        for f,err in errors.items():
            echo('{} {}'.format(f, err))
    else:
        echo('Unexpected Response from server (Code {})'.format(resp.status_code))

@option('--task_id', prompt=True, help='ID of task to delete')
def delete(task_id):
    resp = requests.delete('{}{}'.format(TASKS_DELETE_URL, task_id), json={}, headers=HEADERS )
    if resp.status_code == 204:
        echo('Task Deleted successfully')
    elif resp.status_code == 404:
        echo('Task or endpoint not found')
    else:
        echo('Unexpected Response from server (Code {})'.format(resp.status_code))

def init_commands(group):
    g = group()(task)
    g.add_command( add, name='add')
    #g.command()(add)
    g.command()(fetch)
    g.command()(add)
    g.command()(edit)
    g.command()(delete)