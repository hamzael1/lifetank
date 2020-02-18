
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from passlib.hash import sha256_crypt

db = SQLAlchemy()
ma = Marshmallow()

####### MODEL ########

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    password = db.Column(db.String(254))

    def __repr__(self):
        return '<User %s>' % self.username

    def generate_hash(passwd):
        return sha256_crypt.encrypt(passwd)


def init_db(app, populate_db=False):
    db.init_app(app)
    if populate_db:
        with app.app_context():
            db.drop_all()
            db.create_all()
            u =  UserModel(username='dev-user', password=UserModel.generate_hash('passpass'))
            db.session.add(u)
            db.session.commit()

####### SCHEMA ########

class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username")

def init_schema(app):
    ma.init_app(app)
