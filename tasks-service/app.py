import os
import sys

from flask import Flask

from routes import init_api 
from model import init_db
from flask_jwt_extended import JWTManager

def get_current_env():
    if os.getenv('ENV') == 'PROD':
        return 'PROD'
    elif os.getenv('ENV') == 'DEV' or (len(sys.argv) == 2 and sys.argv[1] == 'dev'):
        return 'DEV'
    elif os.getenv('ENV') == 'TEST' or (len(sys.argv) == 2 and sys.argv[1] == 'test'):
        return 'TEST'
    else:
        return 'DEV' # default to DEV

CURRENT_ENV = get_current_env()

def create_app():
    f = Flask(__name__)
    f.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
    if CURRENT_ENV == 'DEV':
        f.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev.db'
    elif CURRENT_ENV == 'TEST':
        f.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    elif CURRENT_ENV == 'PROD':
        f.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prod.db'
    else:
        raise Exception('Unknown Environment')
    return f


app = create_app()

init_api(app)
init_db(app, populate_db=True if CURRENT_ENV == 'DEV' else False)
jwt = JWTManager(app)


####### RUN APP ########
if __name__ == '__main__':
    DEBUG = False if CURRENT_ENV == 'PROD' else True
    HOST = '0.0.0.0' if CURRENT_ENV == 'PROD' else '127.0.0.1'
    PORT = os.getenv('FLASK_RUN_PORT', 5555)
    app.run(
        debug=DEBUG,
        host=HOST,
        port=PORT
        )