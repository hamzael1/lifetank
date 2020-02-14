from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

tasks = []

class TaskList(Resource):
    def get(self):
        return {'tasks': tasks}
    def post(self):
        return {'message': 'Adding Task'}


class TaskSingle(Resource):
    def get(self, task_id):
        return {'message': 'Getting Task  {}'.format(task_id)}
    def put(self, task_id):
        return {'message': 'Updated Task {}'.format(task_id)}
    def delete(self, task_id):
        return {'message': 'Deleted Task {}'.format(task_id)}

api.add_resource(TaskList, '/tasks/')
api.add_resource(TaskSingle,'/tasks/<string:task_id>/')

if __name__ == '__main__':
    app.run(debug=True)
