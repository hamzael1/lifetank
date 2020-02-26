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


    EXPENSES_SERVICE_HOST = 'expenses'
    EXPENSES_SERVICE_PORT = '8000'
    EXPENSES_SERVICE_URL = 'http://{}:{}'.format(EXPENSES_SERVICE_HOST, EXPENSES_SERVICE_PORT)
    @app.route('/expenses', methods=['GET', 'POST'])
    @app.route('/expenses/<string:expense_id>', methods=['GET', 'PATCH', 'DELETE'])
    @jwt_required
    def expenses(expense_id=None):
        current_user = get_jwt_identity()

        new_body = request.json.copy()
        params_str = ''
        if expense_id is None: 
            if request.method == 'GET': # GET list of all expenses belonging to logged user
                params_array = []
                for param, value in request.args.items():
                    if param != 'owner':
                        params_array.append('{}={}'.format(param, value))

                params_array.append('{}={}'.format('owner', current_user['id']))
                params_str = '&'.join(params_array)
                forward_url = '{}/?{}'.format( EXPENSES_SERVICE_URL, params_str)
            else: # POST new Expense
                new_body['owner_user_id'] = current_user['id']
        else: # GET PATCH DELETE : check if user authorized first
            forward_url = '{}/{}'.format (EXPENSES_SERVICE_URL, expense_id)
            resp = requests.get(forward_url)
            if resp.status_code == 200:
                if resp.json()['owner_user_id'] == current_user['id']:
                    if request.method == 'PATCH':
                        new_body['owner_user_id'] = current_user['id']
                    pass
                else:
                    return make_response(
                        jsonify({'message': 'User unauthorized to perform operation'}),
                        403,
                        {  'Content-Type': 'application/json' }
                    )
            else:
                return make_response(
                        jsonify({'message': 'Something went wrong: couldnt retrieve item'}),
                        resp.status_code,
                        {  'Content-Type': 'application/json' }
                    )
        resp = requests.request(request.method, url=forward_url, json=new_body)
        return make_response(
                resp.content if len(resp.content) > 0 else '',
                resp.status_code,
                { 'Content-Type': 'application/json' }
            )

    TASKS_SERVICE_HOST = 'tasks'
    TASKS_SERVICE_PORT = '8000'
    TASKS_SERVICE_URL = 'http://{}:{}'.format(TASKS_SERVICE_HOST, TASKS_SERVICE_PORT)
    @app.route('/tasks', methods=['GET', 'POST'])
    @app.route('/tasks/<string:task_id>', methods=['GET', 'PATCH', 'DELETE'])
    @jwt_required
    def tasks(task_id=None):
        current_user = get_jwt_identity()

        new_body = request.json.copy()
        params_str = ''
        if task_id is None: 
            if request.method == 'GET': # GET list of all tasks belonging to logged user
                params_array = []
                for param, value in request.args.items():
                    if param != 'owner':
                        params_array.append('{}={}'.format(param, value))

                params_array.append('{}={}'.format('owner', current_user['id']))
                params_str = '&'.join(params_array)
                forward_url = '{}/?{}'.format( TASKS_SERVICE_URL, params_str)
            else: # POST new Expense
                new_body['owner_user_id'] = current_user['id']
        else: # GET PATCH DELETE : check if user authorized first
            forward_url = '{}/{}'.format (TASKS_SERVICE_URL, task_id)
            resp = requests.get(forward_url)
            if resp.status_code == 200:
                if resp.json()['owner_user_id'] == current_user['id']:
                    if request.method == 'PATCH':
                        new_body['owner_user_id'] = current_user['id']
                    pass
                else:
                    return make_response(
                        jsonify({'message': 'User unauthorized to perform operation'}),
                        403,
                        {  'Content-Type': 'application/json' }
                    )
            else:
                return make_response(
                        jsonify({'message': 'Something went wrong: couldnt retrieve item'}),
                        resp.status_code,
                        {  'Content-Type': 'application/json' }
                    )
        resp = requests.request(request.method, url=forward_url, json=new_body)
        return make_response(
                resp.content if len(resp.content) > 0 else '',
                resp.status_code,
                { 'Content-Type': 'application/json' }
            )
