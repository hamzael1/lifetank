
from flask_restful import Resource, Api
from flask import request
from .model import db, TaskModel, TaskSchema



def init_routes(app):
    api = Api(app)

    # Schema instantiation
    task_single_schema = TaskSchema()
    task_list_schema = TaskSchema(many=True)

    @app.route('/dummy', methods=['GET'])
    def dummy():
        return {'message': 'Working'}, 200

    # Api Routes
    class TaskList(Resource):

        def get(self):
            '''
                Get all tasks belonging to a user (specify owner_user_id in URL Param)
            '''
            owner_user_id = request.args.get('owner')
            tasks = TaskModel.query.filter_by(owner_user_id=owner_user_id).all() # Get Tasks of user
            return task_list_schema.dump(tasks)
        
        def post(self):
            task = {
                'title': request.json['title'] if 'title' in request.json else None,
                'comment': request.json['comment'] if 'comment' in request.json else None,
                'due': request.json['due'] if 'due' in request.json else None,
                'done': request.json['done'] if 'done' in request.json else None,
                'owner_user_id': request.json['owner_user_id'] if 'owner_user_id' in request.json else None,
            }
            validation_errors = task_single_schema.validate(task)
            if validation_errors:
                return {'errors': validation_errors}, '400'
            task = task_single_schema.load(task)
            new_task = TaskModel(
                title=task['title'],
                owner_user_id=task['owner_user_id'],
                comment=task['comment'],
                due=task['due'],
                done=task['done'],
            )
            db.session.add(new_task)
            db.session.commit()
            return task_single_schema.dump(new_task), '201'


    class TaskSingle(Resource):
        def get(self, task_id):
            '''
                Get A specific task
            '''
            task = TaskModel.query.get_or_404(task_id)
            if 'check_exists' in request.args:
                return {
                    'exists': True if request.args['check_exists'] else False
                }
            else:
                return task_single_schema.dump(task), '200'

        def patch(self, task_id):
            task = TaskModel.query.get_or_404(task_id)

            request_task = {
                'title': request.json['title'] if 'title' in request.json else None,
                'comment': request.json['comment'] if 'comment' in request.json else None,
                'due': request.json['due'] if 'due' in request.json else None,
                'done': request.json['done'] if 'done' in request.json else None,
                'owner_user_id': request.json['owner_user_id'] if 'owner_user_id' in request.json else None,
            }
            validation_errors = task_single_schema.validate(request_task)
            if validation_errors:
                return {'errors': validation_errors}, '400'
            request_task = task_single_schema.load(request_task)
            task.title = request_task['title']
            task.owner_user_id = request_task['owner_user_id']
            task.comment = request_task['comment']
            task.due = request_task['due']
            task.done = request_task['done']
            db.session.commit()
            return task_single_schema.dump(task), '200'

        def delete(self, task_id):
            task = TaskModel.query.get_or_404(task_id)
            db.session.delete(task)
            db.session.commit()
            return '', '204'

    api.add_resource(TaskList, '/')
    api.add_resource(TaskSingle,'/<string:task_id>')
