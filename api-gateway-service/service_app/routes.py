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
    @app.route('/expenses', methods=['GET', 'POST'])
    @app.route('/expenses/<string:expense_id>', methods=['GET', 'PATCH', 'DELETE'])
    @jwt_required
    def expenses(expense_id=None):
        current_user = get_jwt_identity()
        # perform authorization stuff
        params_array = []
        if expense_id is None:
            for param, value in request.args.items():
                params_array.append('{}={}'.format(param, value))
            params_str = '&'.join(params_array)
            forward_url = '{}/?{}'.format( EXPENSES_SERVICE_URL, params_str) 
        else:
            forward_url = '{}/{}'.format (EXPENSES_SERVICE_URL, expense_id)
        #print(forward_url)
        resp = requests.request(request.method, url=forward_url, json=request.json)
        
        return make_response(
                jsonify(resp.json()) if len(resp.content) > 0 else '',
                resp.status_code
            )