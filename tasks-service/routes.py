
from flask_restful import Resource, Api
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import db, TaskModel, TaskSchema


task_single_schema = TaskSchema()
task_list_schema = TaskSchema(many=True)

####### API ROUTES ########

class TaskList(Resource):
    @jwt_required
    def get(self):
        current_user = get_jwt_identity()
        tasks = TaskModel.query.filter_by(user_id=current_user['id']).all() # Get Tasks of user
        return task_list_schema.dump(tasks)
    
    @jwt_required
    def post(self):
        current_user = get_jwt_identity()
        task = {
            'title': request.json['title'] if 'title' in request.json else None,
            'user_id': current_user['id']
        }
        validation_errors = task_single_schema.validate(task)
        if validation_errors:
            return {'errors': validation_errors}, '400'
        
        new_task = TaskModel(
            title=task['title'],
            user_id=task['user_id']
        )
        db.session.add(new_task)
        db.session.commit()
        return task_single_schema.dump(new_task), '201'


class TaskSingle(Resource):
    @jwt_required
    def get(self, task_id):
        current_user = get_jwt_identity()
        task = TaskModel.query.get_or_404(task_id)

        if task.user_id != current_user['id']:
            return {'message': 'Unauthorized'}, '403'
        else:
            return task_single_schema.dump(task), '200'

    @jwt_required
    def patch(self, task_id):
        task = TaskModel.query.get_or_404(task_id)

        current_user = get_jwt_identity()
        if task.user_id != current_user['id']:
            return {'message': 'Unauthorized'}, '403'
        else:
            request_task = {
                'title': request.json['title'] if 'title' in request.json else None,
                'user_id': current_user['id']
            }
            validation_errors = task_single_schema.validate(request_task)
            if validation_errors:
                return {'errors': validation_errors}, '400'

            task.title = request_task['title']
            db.session.commit()
            return task_single_schema.dump(task), '200'

    @jwt_required
    def delete(self, task_id):
        current_user = get_jwt_identity()
        task = TaskModel.query.get_or_404(task_id)
        if task.user_id != current_user['id']:
            return {'message': 'Unauthorized'}, '403'
        else:
            db.session.delete(task)
            db.session.commit()
            return '', '204'

def init_api(app):
    api = Api(app)
    api.add_resource(TaskList, '/tasks/')
    api.add_resource(TaskSingle,'/tasks/<string:task_id>/')
