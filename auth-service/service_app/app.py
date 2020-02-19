import os
import sys

from flask import Flask

from .model import init_db, populate_db
from .routes import init_routes



def create_app():
    app = Flask(__name__, instance_relative_config=True)
    print('Creating Flask App ({})...'.format(app.config['ENV']))
    # Get Config depending on current ENV 
    # ( set FLASK_ENV environment variable to "development" or "production" ;
    # default is "production" )
    app.config.from_object('service_app.config.{}'.format(app.config['ENV']))
    
    # Init SQLAlchemy DB. Populate DB if env is development
    init_db(app)
    # Populate DB with some dummy users if in dev environment
    if app.config['ENV'] == 'development':
        populate_db(app)

    
    # Init Routes
    init_routes(app)

    return app


