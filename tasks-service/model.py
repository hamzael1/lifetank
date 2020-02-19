
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema, validates, ValidationError


db = SQLAlchemy()

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

class TaskSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True)
    title = fields.Str(required=True)

    @validates("user_id")
    def validate_user_id(self, value):
        if value < 1:
            raise ValidationError('user_id cant be less than 1')
    
    @validates("title")
    def validate_title(self, value):
        if len(value) == 0:
            raise ValidationError('title cant be empty')