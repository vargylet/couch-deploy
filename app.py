"""
Small API that picks up a webhook from Github and processes the data to update
the local repository on the server.
"""
from flask import Flask
from routes.routes import api_endpoint
from utils.logger import logging

app = Flask(__name__)

# Store the logger attribute
logger = logging.logger

# Register flask blueprints
app.register_blueprint(api_endpoint)

if __name__ == '__main__':
    app.run()
