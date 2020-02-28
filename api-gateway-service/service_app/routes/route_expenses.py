from flask import request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests

from .service_endpoints import EXPENSES_SERVICE_URL


@jwt_required
def expenses_requests_handler(expense_id=None):
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
            forward_url = '{}'.format( EXPENSES_SERVICE_URL)
    else: # GET/PATCH/DELETE single Expense: check if user authorized first
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
    if request.method == 'POST' or request.method == 'PATCH':
        task_id = new_body['task_id']
        resp = request.get('{}/?check_exists=True'.format(TASKS_SERVICE_URL))
        if resp.json()['exists'] is False:
            return make_response(
                jsonify({
                    'message': 'Task ID not found'
                })
            )
    resp = requests.request(request.method, url=forward_url, json=new_body)
    return make_response(
            resp.content if len(resp.content) > 0 else '',
            resp.status_code,
            { 'Content-Type': 'application/json' }
        )