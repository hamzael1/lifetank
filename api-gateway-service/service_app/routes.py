from flask import request, jsonify, make_response

from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token, 
                                create_refresh_token,
                                jwt_refresh_token_required,
                                jwt_required,
                                get_jwt_identity)
import requests

from passlib.hash import sha256_crypt


from .model import UserModel, UserSchema

import datetime

def init_routes(app):

    jwt = JWTManager(app)

    user_schema = UserSchema()
    user_list_schema = UserSchema(many=True)

    # Dummy Endpoint for test
    @app.route('/auth/', methods=['GET'])
    def dummy():
        return {'message': 'Please Login'}, 200


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


    EXPENSES_SERVICE_HOST = 'localhost'
    EXPENSES_SERVICE_PORT = '5555'
    EXPENSES_SERVICE_URL = 'http://{}:{}'.format(EXPENSES_SERVICE_HOST, EXPENSES_SERVICE_PORT)
    @app.route('/expenses/', methods=['GET', 'POST'])
    @jwt_required
    def expenses():
        current_user = get_jwt_identity()
        # perform authorization stuff  
        forward_url = '{}/?{}'.format( EXPENSES_SERVICE_URL, request.url.split('?')[1]) 
        # return forward_url, '200'
        resp = requests.request(request.method, url=forward_url, json=request.json)
        #resp_body = resp.get_json()
        #print(resp_body)
        return resp.content, resp.status_code