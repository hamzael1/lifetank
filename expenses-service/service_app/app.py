import os
import sys

from flask import Flask

from .model import init_db, populate_db
from .routes import init_routes



def create_app(testing=False):
    app = Flask(__name__, instance_relative_config=True)
    app.config['TESTING'] = testing
    print('Creating Flask App ({}{})...'.format(app.config['ENV'], ' - Testing' if testing else '')) 
    # Get Config depending on current ENV 
    # ( set FLASK_ENV environment variable to "development" or "production" ;
    # default is "production" )
    app.config.from_object('service_app.config.{}'.format(app.config['ENV']))
    
    # Init SQLAlchemy DB.
    init_db(app)
    # Populate DB with some dummy users if in dev environment
    if app.config['ENV'] == 'development' and not testing:
        populate_db(app, nbr_tasks_per_user=10)

    
    # Init Routes
    init_routes(app)

    return app


