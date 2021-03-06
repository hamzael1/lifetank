
from click import option, echo, password_option, command
import requests
import os
from .settings import HOST, PORT

@command()
@option('--username', prompt=True, default='dev_user_1', help='username to login is mandatory' )
@password_option('--password', default='passpass', confirmation_prompt=False)
def login(username, password):
    assert (username and password), 'Username & Password are mandatory'
    payload = {'username': username, 'password': password}
    LOGIN_URL = 'http://{}:{}/auth/login/'.format(HOST, PORT)
    resp = requests.post(LOGIN_URL, json=payload)
    if resp.status_code == 200:
        echo('Authentication Successful')
        a_token = resp.json()['access_token']
        echo(a_token)
    elif resp.status_code == 401:
        echo('Authentication Failed')
    else:
        echo('Unexpected Response from server (Code {})'.format(resp.status_code))


@command()
def logout():
    echo('Logout ...')
