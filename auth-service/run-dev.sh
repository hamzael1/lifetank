export FLASK_APP=service_app:create_app # accepts the factory function also.
export FLASK_ENV=development
export FLASK_RUN_PORT=8888
export FLASK_DEBUG=1

echo "###### Start running Flask App ... ######"
flask run
