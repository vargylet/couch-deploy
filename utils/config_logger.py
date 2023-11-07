"""
Loading the config and initiating the logging of the app.
"""
import json
import logging
from logging.handlers import RotatingFileHandler

class ConfigLogger:
    """
    This class loads the config file and initiates the logging for the app.

    This class follows the Singleton design pattern to ensure that only one instance of the logger
    configuration is created.

    Methods:
        load_config(self): Load configuration data from 'config.json' into the 'config' attribute.
        init_logger(self): Initialize the logger based on the 'log_level' specified in the config.

    Example usage:
        config_logger = ConfigLogger()  # Get the singleton instance of ConfigLogger.
        # Access the 'config' attribute or the 'logger' attribute for logging
        # configuration and operations.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.load_config()
            cls._instance.init_logger()
        return cls._instance

    def load_config(self):
        """
        Loads the config from the 'config.json' file into the 'config' attribute.
        """
        # Config file
        config_file_name = 'config.json'

        # Reading the configuration file
        try:
            with open(config_file_name, 'r', encoding='utf-8)') as config_file:
                self.config = json.load(config_file)
            logging.info('The config file was loaded successfully')
        except FileNotFoundError:
            logging.critical('The config file could not be found')
        except PermissionError:
            logging.critical('The config file doesn\'t have the right permissions')
        except IOError:
            logging.critical('An I/O error occurred while trying to open the config file')

    def init_logger(self):
        """
        Initiates the logger for the app and loads it into the 'logger' attribute.
        The log level is stored in the config file which is stored in the 'config' attribute.
        """
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
        log_level_str = self.config.get('log_level', 'INFO')
        log_level = log_level_map.get(log_level_str, logging.INFO)
        self.logger.setLevel(log_level)

config_logger = ConfigLogger()
