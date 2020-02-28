export FLASK_APP=service_app:create_app # accepts the factory function also.
export FLASK_ENV=development
export FLASK_RUN_PORT=8888
export FLASK_DEBUG=1
export TASKS_SERVICE_HOST=127.0.0.1
export TASKS_SERVICE_PORT=1111
export EXPENSES_SERVICE_HOST=127.0.0.1
export EXPENSES_SERVICE_PORT=2222
echo "###### Start running Flask App ... ######"
flask run --no-reload
