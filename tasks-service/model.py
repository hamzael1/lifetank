
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()

####### MODEL ########

class TaskModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))

    def __repr__(self):
        return '<Task %s>' % self.title

def init_db(app):
    db.init_app(app)

####### SCHEMA ########

class TaskSchema(ma.Schema):
    class Meta:
        fields = ("id", "title")

def init_schema(app):
    ma.init_app(app)