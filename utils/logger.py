"""
Defining the logger for the application.
"""
import logging
import queue
from logging.handlers import RotatingFileHandler, QueueHandler, QueueListener
from .config_loader import config_loader

class Logger:
    """
    This class loads defines the main logging for the app.

    The class follows the Singleton design pattern to ensure that only one instance of the logger
    configuration is created.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init_logger()
        return cls._instance

    def init_logger(self):
        """
        Initiates the logger for the app and loads it into the 'logger' attribute.
        The log level is stored in the config file which is stored in the 'config' attribute.
        """
        config = config_loader.config

        # Log level mapping to convert config string to logging constant
        log_level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }

        # Log file to store logs
        log_file_name = 'couch-deploy.log'

        # Creating logger for the app
        self.logger = logging.getLogger(__name__)

        # Set log level for opening the config file
        self.logger.setLevel(logging.INFO)

        # Adding file handler to write the logs to file
        file_handler = RotatingFileHandler(log_file_name, maxBytes=100000, backupCount=5)

        # Defining the formatting of the logging
        log_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)'
        )
        file_handler.setFormatter(log_format)

        # Adding file handler to logger
        self.logger.addHandler(file_handler)

        # Set log level based on config file
        log_level_str = config.get('log_level', 'INFO')
        log_level = log_level_map.get(log_level_str, logging.INFO)
        self.logger.setLevel(log_level)

        # Creating a queue to handle log messages
        log_queue = queue.Queue(-1)
        queue_handler = QueueHandler(log_queue)
        self.logger.addHandler(queue_handler)

        # Adding QueueListener to handle log messages from multiple processes
        queue_listener = QueueListener(log_queue, file_handler)
        queue_listener.start()

        self.logger.info("Logging has been successfully initiated during startup.")

logging = Logger()
