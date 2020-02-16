import os
import sys

from flask import Flask, request
from flask_restful import Resource, Api

from model import db, ma, TaskModel, TaskSchema

def get_current_env():

    if os.getenv('ENV') == 'PROD':
        return 'PROD'
    else:
        return 'DEV_TEST'
CURRENT_ENV = get_current_env()

def create_app():
    f = Flask(__name__)
    
    if CURRENT_ENV == 'DEV_TEST':
        f.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev_test.db'
    elif CURRENT_ENV == 'PROD':
        f.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prod.db'
    else:
        raise Exception('Unknown Environment')
    return f


app = create_app()
api = Api(app)
ma.init_app(app)

db.init_app(app)


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

api.add_resource(TaskList, '/tasks/')
api.add_resource(TaskSingle,'/tasks/<string:task_id>/')



####### RUN APP ########
if __name__ == '__main__':
    app.run(debug=True)