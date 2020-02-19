from flask import request, jsonify

from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token, 
                                create_refresh_token,
                                jwt_refresh_token_required,
                                get_jwt_identity)

from passlib.hash import sha256_crypt


from .model import init_schema, UserModel, UserSchema

import datetime

def init_routes(app):

    jwt = JWTManager(app)

    user_schema = UserSchema()
    user_list_schema = UserSchema(many=True)

    # TODO: REMOVE !
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