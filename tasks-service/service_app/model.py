
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema, validates, ValidationError

from datetime import datetime, timedelta

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


def populate_db(app, user_ids=[1000,1001], nbr_tasks_per_user=5):
    """
        Populate DB with "nbr_tasks" tasks
    """
    print('Populating ...')
    with app.app_context():
        db.drop_all()
        db.create_all()
        today = datetime.today()
        for uid in user_ids:
            for i in range(nbr_tasks_per_user):
                t =  TaskModel( 
                    user_id=uid,
                    title='Task Title {}'.format(i),
                    comment='Comment for Task {}'.format(i),
                    due=today + timedelta(days=randrange(1,100)),
                    done=True if rand() > 0.5 else False
                    )
                db.session.add(t)
        db.session.commit()