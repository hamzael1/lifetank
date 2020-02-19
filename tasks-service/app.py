import os
import sys

from flask import Flask

from routes import init_api 
from model import init_db
from flask_jwt_extended import JWTManager

def get_current_env():
    if os.getenv('ENV') == 'PROD':
        return 'PROD'
    elif len(sys.argv) == 2 and sys.argv[1] == 'dev':
        return 'DEV'
    else:
        return 'TEST'

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
    app.run(debug=False if CURRENT_ENV == 'PROD' else True)