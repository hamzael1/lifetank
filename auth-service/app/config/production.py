import datetime

JWT_SECRET_KEY = 'jwt-secret-string'
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=15)
JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=3)

SQLALCHEMY_DATABASE_URI = 'sqlite:///prod.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
