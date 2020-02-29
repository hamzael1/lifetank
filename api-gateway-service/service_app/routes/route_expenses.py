from flask import request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests



@jwt_required
def expenses_requests_handler(expense_id=None):
    from .helpers import user_has_right_to_add_expense_to_task
    from .service_endpoints import EXPENSES_SERVICE_URL

    current_user = get_jwt_identity()

    new_body = request.json.copy()
    
    if (not 'task_id' in new_body) or (new_body['task_id'] is None):
        new_body['task_id'] = 0 
    
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
            if not user_has_right_to_add_expense_to_task(current_user['id'], new_body['task_id']):
                return make_response(
                    jsonify({'message': 'Could not write expense for Task provided ( either because it does not exist or because user is not authorized )'}),
                    403,
                    {  'Content-Type': 'application/json' }
                )
            new_body['owner_user_id'] = current_user['id']
            forward_url = '{}'.format( EXPENSES_SERVICE_URL)
    else: # GET/PATCH/DELETE single Expense: check if user authorized first
        forward_url = '{}/{}'.format (EXPENSES_SERVICE_URL, expense_id)
        if user_has_right_to_add_expense_to_task(current_user['id'], new_body['task_id']):
            if request.method == 'PATCH':
                if not user_has_right_to_add_expense_to_task(current_user['id'], new_body['task_id']):
                    return make_response(
                        jsonify({'message': 'Could not write expense for Task provided ( either because it does not exist or because user is not authorized )'}),
                        403,
                        {  'Content-Type': 'application/json' }
                        )
                new_body['owner_user_id'] = current_user['id']
            pass
        else:
            return make_response(
                jsonify({'message': 'User unauthorized to perform operation'}),
                403,
                {  'Content-Type': 'application/json' }
            )

    # Main Reroute Request
    resp = requests.request(request.method, url=forward_url, json=new_body)
    return make_response(
            resp.content if len(resp.content) > 0 else '',
            resp.status_code,
            { 'Content-Type': 'application/json' }
        )