from click import echo, group, argument, option
import requests
from commands import expenses

from commands.auth import login as login_command, logout as logout_command
from commands.tasks import task as task_group
from commands.expenses import expense as expense_group

@group()
def cli():
    echo('LifeTank')

cli.add_command(login_command, name='login')
cli.add_command(logout_command, name='logout')
cli.add_command(task_group, name='tasks')
cli.add_command(expense_group, name='expenses')


