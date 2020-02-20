
from flask_restful import Resource, Api
from flask import request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from .model import db, TaskModel, TaskSchema



def init_routes(app):
    api = Api(app)
    jwt = JWTManager(app)

    # Schema instantiation
    task_single_schema = TaskSchema()
    task_list_schema = TaskSchema(many=True)

    # Api Routes
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
                'comment': request.json['comment'] if 'comment' in request.json else None,
                'due': request.json['due'] if 'due' in request.json else None,
                'done': request.json['done'] if 'done' in request.json else None,
                'user_id': current_user['id']
            }
            validation_errors = task_single_schema.validate(task)
            if validation_errors:
                return {'errors': validation_errors}, '400'
            task = task_single_schema.load(task)
            new_task = TaskModel(
                title=task['title'],
                user_id=task['user_id'],
                comment=task['comment'],
                due=task['due'],
                done=task['done'],
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
                    'comment': request.json['comment'] if 'comment' in request.json else None,
                    'due': request.json['due'] if 'due' in request.json else None,
                    'done': request.json['done'] if 'done' in request.json else None,
                    'user_id': current_user['id']
                }
                validation_errors = task_single_schema.validate(request_task)
                if validation_errors:
                    return {'errors': validation_errors}, '400'
                request_task = task_single_schema.load(request_task)
                task.title = request_task['title']
                task.comment = request_task['comment']
                task.due = request_task['due']
                task.done = request_task['done']
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

    api.add_resource(TaskList, '/tasks/')
    api.add_resource(TaskSingle,'/tasks/<string:task_id>/')
