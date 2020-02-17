import os
import sys

from flask import Flask

from routes import init_api 
from model import init_db, init_schema

def get_current_env():

    if os.getenv('ENV') == 'PROD':
        return 'PROD'
    else:
        return 'DEV_TEST'
CURRENT_ENV = get_current_env()

def create_app():
    f = Flask(__name__)
    
    if CURRENT_ENV == 'DEV_TEST':
        f.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev_test.db'
    elif CURRENT_ENV == 'PROD':
        f.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prod.db'
    else:
        raise Exception('Unknown Environment')
    return f


app = create_app()

init_api(app)
init_schema(app)
init_db(app)



####### RUN APP ########
if __name__ == '__main__':
    app.run(debug=False if CURRENT_ENV == 'PROD' else True)