
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
        new_task = TaskModel(
            title=request.json['title'],
            user_id=current_user['id']
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
        current_user = get_jwt_identity()
        task = TaskModel.query.get_or_404(task_id)

        if task.user_id != current_user['id']:
            return {'message': 'Unauthorized'}, '403'
        else:
            if 'title' in request.json:
                task.title = request.json['title']

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
