import requests

from .service_endpoints import TASKS_SERVICE_URL

def user_has_right_to_add_expense_to_task(user_id, task_id):
    if task_id is None or task_id == 0:
        return True # Expense has no task, no problem
    path = '/{}'.format(task_id)
    resp = requests.get('{}{}'.format(TASKS_SERVICE_URL, path))
    return (resp.status_code == 200) and (resp.json()['owner_user_id'] == user_id)
