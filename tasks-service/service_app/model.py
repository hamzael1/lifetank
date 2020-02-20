
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema, validates, ValidationError

from datetime import datetime

from random import random as rand, randrange, choice


db = SQLAlchemy()

####### MODEL ########

class TaskModel(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(64), nullable=False)
    comment = db.Column(db.String(255), default='')
    due = db.Column(db.DateTime, nullable=False)
    done = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime, default=datetime.today())

    def __repr__(self):
        return '<Task %s>' % self.title

####### SCHEMA ########

class TaskSchema(Schema):
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


####### FUNCTIONS ########

def init_db(app):
    db.init_app(app)


def populate_db(app, nbr_tasks=10, user_ids=[1000,1001]):
    """
        Populate DB with "nbr_tasks" tasks
    """
    print('Populating ...')
    with app.app_context():
        db.drop_all()
        db.create_all()
        for i in range(nbr_tasks):
            t =  TaskModel( 
                user_id=choice(user_ids),
                title='Task Title Dev {}'.format(i),
                comment='Comment for Task Dev {}'.format(i),
                due=datetime(2020, randrange(1,12), randrange(1,27)),
                done=True if rand() > 0.5 else False
                )
            db.session.add(t)
        db.session.commit()