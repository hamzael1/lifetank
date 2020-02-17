
from flask_restful import Resource, Api
from flask import request
from model import db, TaskModel, TaskSchema


task_single_schema = TaskSchema()
task_list_schema = TaskSchema(many=True)

####### API ROUTES ########

class TaskList(Resource):
    def get(self):
        tasks = TaskModel.query.all()
        return task_list_schema.dump(tasks)
    def post(self):
        new_task = TaskModel(
            title=request.json['title'],
        )
        db.session.add(new_task)
        db.session.commit()
        return task_single_schema.dump(new_task), '201'


class TaskSingle(Resource):
    def get(self, task_id):
        task = TaskModel.query.get_or_404(task_id)
        return task_single_schema.dump(task), '200'

    def patch(self, task_id):
        task = TaskModel.query.get_or_404(task_id)

        if 'title' in request.json:
            task.title = request.json['title']

        db.session.commit()
        return task_single_schema.dump(task), '200'

    def delete(self, task_id):
        task = TaskModel.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return '', '204'

def init_api(app):
    api = Api(app)
    api.add_resource(TaskList, '/tasks/')
    api.add_resource(TaskSingle,'/tasks/<string:task_id>/')
