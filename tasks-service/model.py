
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema, validates, ValidationError

from datetime import datetime

from random import random as rand, randrange
db = SQLAlchemy()

####### MODEL ########

class TaskModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(64), nullable=False)
    comment = db.Column(db.String(255), default='')
    due = db.Column(db.DateTime, nullable=False)
    done = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime, default=datetime.today())

    def __repr__(self):
        return '<Task %s>' % self.title

def init_db(app, populate_db=False):
    db.init_app(app)
    if populate_db:
        with app.app_context():
            db.drop_all()
            db.create_all()
            for i in range(5):
                t = TaskModel( 
                    title='Task Test {}'.format(i+1),
                    user_id=1000,
                    comment='Comment for Task Test {}'.format(i+1),
                    done=True if rand() > 0.5 else False,
                    due=datetime(2020,randrange(2,6), randrange(1,26))
                )
                db.session.add(t)
            for i in range(5):
                t = TaskModel( 
                    title='Task Test {}'.format(i+1),
                    user_id=1001,
                    comment='Comment for Task Test {}'.format(i+1),
                    done=True if rand() > 0.5 else False,
                    due=datetime(2020,randrange(2,6), randrange(1,26))
                )
                db.session.add(t)
            db.session.commit()

####### SCHEMA ########

class TaskSchema(Schema):
    __tablename__ = 'tasks'

    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True)
    title = fields.Str(required=True)
    comment = fields.Str(required=True)
    due = fields.DateTime(required=True, format='iso')
    done = fields.Bool(required=True)
    created = fields.DateTime(dump_only=True, format='iso')

    @validates("user_id")
    def validate_user_id(self, value):
        if value < 1:
            raise ValidationError('user_id cant be less than 1')
    
    @validates("title")
    def validate_title(self, value):
        if len(value) == 0:
            raise ValidationError('title cant be empty')