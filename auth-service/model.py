
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()

####### MODEL ########

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    password = db.Column(db.String(254))

    def __repr__(self):
        return '<User %s>' % self.username

def init_db(app):
    db.init_app(app)

####### SCHEMA ########

class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username")

def init_schema(app):
    ma.init_app(app)
