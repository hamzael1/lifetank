import pytest
import requests
from model import db, UserModel
from app import app

ROOT_URL = 'http://localhost:8888/auth'


def populate_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        u = UserModel(username='test_user', password='test_pass')
        db.session.add(u)
        db.session.commit()

@pytest.fixture(scope='module', autouse=True)
def init_db_for_test_session(request):
    populate_db()
    def fin():
        pass
        with app.app_context():
            db.drop_all()
    request.addfinalizer(fin)


def test_login():
    """
        TEST POST Request to Login
    """
    response = requests.post('{}/login/'.format(ROOT_URL), json={'username': 'test_user'})
    assert response.status_code == 200