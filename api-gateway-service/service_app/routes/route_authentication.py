
from flask import request

from flask_jwt_extended import (create_access_token, 
                                create_refresh_token,
                                jwt_refresh_token_required,
                                jwt_required,
                                get_jwt_identity)

from ..model import UserModel, UserSchema

from passlib.hash import sha256_crypt



def login_request_handler():
    user_schema = UserSchema()
    validation_errors = user_schema.validate(request.json)
    if validation_errors:
        return {'errors': validation_errors}, 400
    req_username = request.json['username']
    res = UserModel.query.filter_by(username=req_username).all()
    if not res:
        return {'message': 'Authentication with provided credentials failed'}, 401
    else:
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