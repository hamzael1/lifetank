from click import echo, group, argument, option
import requests

from commands.auth import init_commands as auth_init_commands
from commands.tasks import init_commands as tasks_init_commands
from commands.expenses import init_commands as expenses_init_commands

@group()
def cli():
    echo('cc')

auth_init_commands(cli.command)
tasks_init_commands(cli.group)
expenses_init_commands(cli.group)