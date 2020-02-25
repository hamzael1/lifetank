
from flask_sqlalchemy import SQLAlchemy
#from flask_marshmallow import Marshmallow

from marshmallow import fields, Schema, validates, ValidationError

from passlib.hash import sha256_crypt

db = SQLAlchemy()

####### MODEL ########

class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    password = db.Column(db.String(254))

    def __repr__(self):
        return '<User %s>' % self.username

    def generate_hash(passwd):
        return sha256_crypt.hash(passwd)



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


####### FUNCTIONS ########

def init_db(app, populate_db_param=False):
    db.init_app(app)


def populate_db(app, users):
    """
        Create users.
        [
            { 'username': ..., 'password': ... }, 
            { 'username': ..., 'password': ... }, 
        ]
    """
    with app.app_context():
        db.drop_all()
        db.create_all()
        for u in users:
            u =  UserModel(
                id=u['id'],
                username=u['username'],
                password=UserModel.generate_hash(u['password']))
            db.session.add(u)
        db.session.commit()