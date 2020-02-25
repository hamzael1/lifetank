
import pytest

from service_app.model import UserModel

from conftest import TEST_USERS

ROOT_URL = '/auth'

def test_dummy(app_client):
    response = app_client.get('{}/'.format(ROOT_URL))
    assert response.status_code == 200
    resp_body = response.get_json()
    assert 'message' in resp_body
    assert resp_body['message'] == 'Please Login'


class TestLogin:

    LOGIN_URL = '{}/login/'.format(ROOT_URL)

    @pytest.mark.parametrize("test_user", TEST_USERS)
    def test_login__success(self, app_client, test_user):
        """
            TEST POST Request to Login for all users in DB : Success case
        """
        response = app_client.post (
            TestLogin.LOGIN_URL,
            json = {
                'username': test_user['username'],
                'password': test_user['password']
            }
        )
        assert response.status_code == 200
        resp_body = response.get_json()
        assert 'access_token' in resp_body, 'Expected access token in response body'
        assert len(resp_body['access_token']) > 0, 'Expected access token length to be bigger than 0'
        assert 'refresh_token' in resp_body, 'Expected refresh token in response body'
        assert len(resp_body['refresh_token']) > 0, 'Expected refresh token length to be bigger than 0'


    def test_login__bad_request(self, app_client):
        """
            TEST POST Invalid Request to Login
            Cases: No password, No username, Password too small, username too small
        """
        response = app_client.post (
            TestLogin.LOGIN_URL,
            json = {
                'username': 'user' # No password !
            }
        )
        assert response.status_code == 400, 'Expecting Invalid Request when no password is provided in Request'
        response = app_client.post (
            TestLogin.LOGIN_URL,
            json = {
                'password': 'passpass' # No username !
            }
        )
        assert response.status_code == 400, 'Expecting Invalid Request when no username is provided in Request'

        response = app_client.post (
            TestLogin.LOGIN_URL,
            json = {
                'username': 'user',
                'password': '123' # Password too small !
            }
        )
        assert response.status_code == 400, 'Expecting Invalid Request when password with lenth < 8 is provided in Request'
        response = app_client.post (
            TestLogin.LOGIN_URL,
            json = {
                'username': 'u', # username too small !
                'password': 'passpass'
            }
        )
        assert response.status_code == 400, 'Expecting Invalid Request when no username with length < 2 is provided in Request'


    def test_login__wrong_password(self, app_client, random_test_user):
        """
            TEST POST Request to Login Failure case
        """
        response = app_client.post (
            TestLogin.LOGIN_URL,
            json = {
                'username': random_test_user['username'],
                'password': 'wrong_password'
            }
        )
        assert response.status_code == 401

def test_refresh_token__success(app_client, random_test_user):
    """
        TEST POST Request to Get new Access token using REfresh token
        STEP 1: login and get access and refresh tokens
        STEP 2: request a new access token using the refresh token from step 1
    """
    # STEP 1
    response = app_client.post (
        TestLogin.LOGIN_URL,
        json = {
            'username': random_test_user['username'],
            'password': random_test_user['password']
        }
    )
    assert response.status_code == 200
    resp_body = response.get_json()
    assert 'access_token' in resp_body, 'Expected access token in response body'
    assert 'refresh_token' in resp_body, 'Expected refresh token in response body'
    refresh_token = resp_body['refresh_token']
    # STEP 2
    response = app_client.post(
        '{}/refresh/'.format(ROOT_URL),
        headers={'Authorization': 'Bearer {}'.format(refresh_token)}
    )
    assert response.status_code == 200
    resp_body = response.get_json()
    assert 'access_token' in resp_body, 'Expected access token in response body'