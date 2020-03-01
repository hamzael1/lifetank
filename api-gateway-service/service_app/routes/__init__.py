from flask_jwt_extended import JWTManager

from .route_authentication import login_request_handler
from .route_tasks import tasks_requests_handler
from .route_expenses import expenses_requests_handler



def init_routes(app):

    from .paths import PATHS

    # Dummy Endpoint for test
    @app.route(PATHS['DUMMY'], methods=['GET'])
    def dummy():
        return {'message': 'Dummy path working'}, 200
    

    # Authentication Endpoints
    jwt = JWTManager(app)
    app.route(PATHS['LOGIN'], methods=['POST'])(login_request_handler)

    # Tasks Endpoints
    app.route(PATHS['TASK_LIST_TODAY'], methods=['GET', 'POST'])(tasks_requests_handler)
    app.route(PATHS['TASK_LIST_ALL'], methods=['GET', 'POST'])(tasks_requests_handler)
    app.route(PATHS['TASK_SINGLE'], methods=['GET', 'PATCH', 'DELETE'])(tasks_requests_handler)

    # Expenses Endpoints
    app.route(PATHS['EXPENSE_LIST'], methods=['GET', 'POST'])(expenses_requests_handler)
    app.route(PATHS['EXPENSE_SINGLE'], methods=['GET', 'PATCH', 'DELETE'])(expenses_requests_handler)
