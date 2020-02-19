
from flask_sqlalchemy import SQLAlchemy
#from flask_marshmallow import Marshmallow

from marshmallow import fields, Schema, validates, ValidationError

from passlib.hash import sha256_crypt

db = SQLAlchemy()
#ma = Marshmallow()

####### MODEL ########

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    password = db.Column(db.String(254))

    def __repr__(self):
        return '<User %s>' % self.username

    def generate_hash(passwd):
        return sha256_crypt.hash(passwd)


def init_db(app, populate_db=False):
    db.init_app(app)
    # Create 2 users in DB with same password and ids 1000, 1001
    if populate_db:
        with app.app_context():
            db.drop_all()
            db.create_all()
            u =  UserModel(id=1000, username='dev-user-1', password=UserModel.generate_hash('passpass'))
            db.session.add(u)
            u =  UserModel(id=1001, username='dev-user-2', password=UserModel.generate_hash('passpass'))
            db.session.add(u)
            db.session.commit()

####### SCHEMA ########

class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

    @validates('username')
    def validate_username(self, value):
        if len(value) < 2:
            raise ValidationError("Username must be at least 2 charachters long")
    @validates('password')
    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 charachters long")

def init_schema(app):
    ma.init_app(app)
