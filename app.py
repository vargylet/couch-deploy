"""
Small API that picks up a webhook from Github and processes the data to update
the local repository on the server.
"""
from flask import Flask#, request
from routes.routes import api_endpoint
from utils.config_logger import config_logger

app = Flask(__name__)

# Loading the config
config = config_logger.config
# Initalizing the logger
logger = config_logger.logger

# Register flask blueprints
app.register_blueprint(api_endpoint)

logger.info('The app started successfully. Waiting for signals...')

if __name__ == '__main__':
    app.run()
