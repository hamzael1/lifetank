import os
import sys

from flask import Flask, request, jsonify

from model import init_db, UserModel, UserSchema

from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token, 
                                create_refresh_token,
                                jwt_refresh_token_required,
                                get_jwt_identity)

from passlib.hash import sha256_crypt

import datetime

def get_current_env():
    if os.getenv('ENV') == 'PROD':
        return 'PROD'
    elif len(sys.argv) == 2 and sys.argv[1] == 'dev':
        return 'DEV'
    else:
        return 'TEST'

CURRENT_ENV = get_current_env()
print(CURRENT_ENV)

def create_app():
    f = Flask(__name__)
    f.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
    f.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=180 if CURRENT_ENV != 'PROD' else 15)
    f.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(days=3)
    
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

#init_schema(app)
init_db(app, populate_db=True if CURRENT_ENV != 'PROD' else False)
jwt = JWTManager(app)

user_schema = UserSchema()
user_list_schema = UserSchema(many=True)

@app.route('/users/', methods=['GET'])
def get_users():
    users = UserModel.query.all()
    return jsonify(user_list_schema.dump(users))

@app.route('/auth/login/', methods=['POST'])
def login():
    validation_errors = user_schema.validate(request.json)
    if validation_errors:
        return {'errors': validation_errors}, 400
    req_username = request.json['username']
    res = UserModel.query.filter_by(username=req_username).all()
    if len(res) == 1:
        db_user = res[0].__dict__
        db_user_password = db_user['password']
        req_password = request.json['password']
        if sha256_crypt.verify(req_password, db_user_password) == True:
            return {
                'access_token': create_access_token(identity = {'id': db_user['id'], 'username': db_user['username']} ),
                'refresh_token': create_refresh_token(identity = {'id': db_user['id'], 'username': db_user['username']} )
                }, 200
        else:
            return {'message': 'auth failed'}, 401
    else:
        return {'message': 'auth failed'}, 401

@app.route('/auth/refresh/', methods=['POST'])
@jwt_refresh_token_required
def token_refresh():
    current_user = get_jwt_identity()
    return {
        'access_token': create_access_token(identity=current_user)
    }


DEBUG = False if CURRENT_ENV == 'PROD' else True
PORT = 8888 if CURRENT_ENV == 'PROD' else 8888

####### RUN APP ########
if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT)