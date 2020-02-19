import os
import sys

from flask import Flask

from .model import init_db
from .routes import init_routes



def create_app():
    print('Creating Flask App ...')
    app = Flask(__name__, instance_relative_config=True)
    # Get Config depending on current ENV 
    # ( set FLASK_ENV environment variable to "development" or "production" ;
    # default is "production" )
    app.config.from_object('app.config.{}'.format(app.config['ENV']))
    
    # Init SQLAlchemy DB. Populate DB if env is development
    init_db(app, populate_db=True if app.config['ENV'] == 'development' else False)
    
    # Init Routes
    init_routes(app)

    return app


