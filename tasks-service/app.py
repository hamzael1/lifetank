from flask import Flask, request
from flask_restful import Resource, Api

from flask_sqlalchemy import SQLAlchemy

from flask_marshmallow import Marshmallow

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

app = create_app()
db = SQLAlchemy(app)
api = Api(app)
ma = Marshmallow(app)


####### MODEL ########

class TaskModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))

    def __repr__(self):
        return '<Task %s>' % self.title

####### SCHEMA ########

class TaskSchema(ma.Schema):
    class Meta:
        fields = ("id", "title")

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
        return task_single_schema.dump(task)

    def patch(self, task_id):
        task = TaskModel.query.get_or_404(task_id)

        if 'title' in request.json:
            task.title = request.json['title']

        db.session.commit()
        return task_single_schema.dump(task)

    def delete(self, task_id):
        task = TaskModel.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return '', 204

api.add_resource(TaskList, '/tasks/')
api.add_resource(TaskSingle,'/tasks/<string:task_id>/')



####### RUN APP ########
if __name__ == '__main__':
    app.run(debug=True)