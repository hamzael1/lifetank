def login():
    echo('Login ...')


def logout():
    echo('Logout ...')

def init_commands(command):
    command()(login)
    command()(logout)