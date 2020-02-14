from flask import Flask, request
from flask_restful import Resource, Api

from flask_marshmallow import Marshmallow 

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

db = SQLAlchemy(app)
api = Api(app)
ma = Marshmallow(app) # new

class TaskModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))

    def __repr__(self):
        return '<Task %s>' % self.title

class TaskSchema(ma.Schema):
    class Meta:
        fields = ("id", "title")

task_single_schema = TaskSchema()
task_list_schema = TaskSchema(many=True)

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
        return task_single_schema.dump(new_task)

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