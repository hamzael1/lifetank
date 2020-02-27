# Microservices 101

This project is a Todo/Expenses App built using microservices (API Gateway) paradigm.
Each Microservice is a standalone Flask App with its own Persistence and Tests.
Everything is containerized and deployed using Docker / docker-compose.

In order to run it: docker-compose up --build

Libraries used: Flask, Flask-restful, Flask-SQLAlchemy, Marshmallow, Flask-JWT-Extended