export FLASK_APP=app:create_app
export FLASK_ENV=development
export FLASK_RUN_PORT=8888
export FLASK_DEBUG=1

echo "###### Start running Flask App ... ######"
flask run