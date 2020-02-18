import pytest
import requests
from model import db, UserModel
from app import app

from passlib.hash import sha256_crypt

ROOT_URL = 'http://localhost:8888/auth'

@pytest.fixture(scope='session', autouse=False)
def test_user():
    return {
        'username': 'test_user',
        'password': 'test_pass'
    }

def populate_db(test_user):
    with app.app_context():
        db.drop_all()
        db.create_all()
        u = UserModel (
                username=test_user['username'],
                password=sha256_crypt.encrypt(test_user['password'])
            )
        db.session.add(u)
        db.session.commit()

@pytest.fixture(scope='module', autouse=True)
def init_db_for_test_session(request, test_user):
    populate_db(test_user)
    def fin():
        pass
        with app.app_context():
            db.drop_all()
    request.addfinalizer(fin)


def test_login_success(test_user):
    """
        TEST POST Request to Login Success case
    """
    response = requests.post (
        '{}/login/'.format(ROOT_URL),
        json = {
            'username': test_user['username'],
            'password': test_user['password']
        }
    )
    assert response.status_code == 200
    resp_body = response.json()
    assert 'access_token' in resp_body, 'Expected access token in response body'
    assert len(resp_body['access_token']) > 0, 'Expected access token length to be bigger than 0'
    assert 'refresh_token' in resp_body, 'Expected refresh token in response body'
    assert len(resp_body['refresh_token']) > 0, 'Expected refresh token length to be bigger than 0'

def test_login_failure(test_user):
    """
        TEST POST Request to Login Failure case
    """
    response = requests.post (
        '{}/login/'.format(ROOT_URL),
        json = {
            'username': test_user['username'],
            'password': 'wrong_password'
        }
    )
    assert response.status_code == 401

def test_refresh_token__success(test_user):
    """
        TEST POST Request to Get new Access token using REfresh token
        STEP 1: login and get access and refresh tokens
        STEP 2: request a new access token using the refresh token from step 1
    """
    # STEP 1
    response = requests.post (
        '{}/login/'.format(ROOT_URL),
        json = {
            'username': test_user['username'],
            'password': test_user['password']
        }
    )
    assert response.status_code == 200
    resp_body = response.json()
    assert 'access_token' in resp_body, 'Expected access token in response body'
    assert 'refresh_token' in resp_body, 'Expected refresh token in response body'
    refresh_token = resp_body['refresh_token']
    # STEP 2
    response = requests.post(
        '{}/refresh/'.format(ROOT_URL),
        headers={'Authorization': 'Bearer {}'.format(refresh_token)}
    )
    assert response.status_code == 200
    resp_body = response.json()
    assert 'access_token' in resp_body, 'Expected access token in response body'
