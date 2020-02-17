import os
import sys

from flask import Flask, request

from model import init_db, init_schema, UserModel

from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token, 
                                create_refresh_token,
                                jwt_required,
                                jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)
def get_current_env():
    if os.getenv('ENV') == 'PROD':
        return 'PROD'
    else:
        return 'DEV_TEST'
CURRENT_ENV = get_current_env()

def create_app():
    f = Flask(__name__)
    f.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
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
jwt = JWTManager(app)


@app.route('/auth/login/', methods=['POST'])
def login():
    req_username = request.json['username']
    res = UserModel.query.filter_by(username=req_username).all()
    if len(res) == 1:
        req_password = request.json['password']
        user = res[0].__dict__
        if user['password'] == req_password:
            return {
                'status': 'success',
                'access_token': create_access_token(identity = request.json['username']),
                'refresh_token': create_refresh_token(identity = request.json['username'])
                }, 200
        else:
            return {'message': 'auth failed'}, 401
    else:
        return {'message': 'auth failed'}, 401




DEBUG = False if CURRENT_ENV == 'PROD' else True
PORT = 8888 if CURRENT_ENV == 'PROD' else 8888

####### RUN APP ########
if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT)