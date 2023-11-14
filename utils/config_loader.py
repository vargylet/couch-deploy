"""
Handling of the config file.
"""
import logging
import yaml

class ConfigLoader:
    """
    This class loads the config file for the app and logs the action or any errors.
    The class follows the Singleton design pattern to ensure that the config is loaded once.

    Methods:
        load_config(self): Load configuration data from 'config.json' into the 'config' attribute.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.load_config()
        return cls._instance

    def load_config(self):
        """
        Loads the config from the 'config.json' file into the 'config' attribute.
        """
        # Config file
        config_file_name = 'config/app_config.yml'

        # Reading the configuration file
        try:
            with open(config_file_name, 'r', encoding='utf-8)') as config_file:
                self.config = yaml.safe_load(config_file)
            logging.info('%s was loaded successfully.', config_file_name)
        except FileNotFoundError:
            logging.critical('The config file could not be found.')
        except PermissionError:
            logging.critical('The config file doesn\'t have the right permissions.')
        except IOError:
            logging.critical('An I/O error occurred while trying to open the config file.')

config_loader = ConfigLoader()
