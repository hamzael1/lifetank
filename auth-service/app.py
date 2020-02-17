import os
import sys

from flask import Flask, request

from model import init_db, init_schema, UserModel

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

init_schema(app)
init_db(app)


@app.route('/auth/login/', methods=['POST'])
def login():
    username = request.json['username']
    res = UserModel.query.filter_by(username=username).all()
    if len(res) == 1:
        return {'status': 'success'}, 200
    else:
        return {'status': 'auth failed'}, 401




DEBUG = False if CURRENT_ENV == 'PROD' else True
PORT = 8888 if CURRENT_ENV == 'PROD' else 8888

####### RUN APP ########
if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT)