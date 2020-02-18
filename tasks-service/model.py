
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()

####### MODEL ########

class TaskModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    title = db.Column(db.String(64))

    def __repr__(self):
        return '<Task %s>' % self.title

def init_db(app, populate_db=False):
    db.init_app(app)
    if populate_db:
        with app.app_context():
            db.drop_all()
            db.create_all()
            for i in range(5):
                t = TaskModel( title='Task dev %s' % i, user_id=1000)
                db.session.add(t)
            for i in range(5):
                t = TaskModel( title='Task dev %s' % i, user_id=1001)
                db.session.add(t)
            db.session.commit()

####### SCHEMA ########

class TaskSchema(ma.Schema):
    class Meta:
        fields = ("id", "user_id", "title")

def init_schema(app):
    ma.init_app(app)
