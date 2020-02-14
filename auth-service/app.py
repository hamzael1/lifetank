
from flask import Flask, url_for, jsonify, request

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def index():
    return jsonify({'message': 'Welcome to this microservice',
                    'status': 'success'})
