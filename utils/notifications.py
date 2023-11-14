"""
This module loads, initiates, and configures the Apprise library.
It is used to send human readable notifications. 
"""
from apprise import Apprise, AppriseConfig, NotifyType
from .logger import logging
from .config_loader import config_loader

class Notifications():
    """
    The class initates the notification object using Apprise.
    It provides custom methods for the notification types (notify_type) to simplify
    the code in the rest of the application. The naming of the methods are the
    same as Apprise uses.
    """
    def __init__(self):
        """
        Loads the apprise config object and the notification configuration.
        Then it adds the configuration to the apprise object.
        """
        # Store the logger attribute
        logger = logging.logger
        # Store the config attribute
        config = config_loader.config

        # Creating a dictionary for the notification levels
        notification_levels_dict = {
            'INFO': 10,
            'SUCCESS': 20,
            'WARNING': 30,
            'FAILURE': 40
        }
        # Store the notification level based on config and dictionary
        self.notify_level = notification_levels_dict.get(config['notification_level'], 20)

        # Initiate apprice object
        self.notification_object = Apprise()
        # Initiate apprise config object
        apprise_config = AppriseConfig()
        # Add config from notification config file
        apprise_config.add('config/notifications.yml')
        # Add apprise config to apprise object
        self.notification_object.add(apprise_config)

        # Storing the number of notification services configured
        self.loaded_services = len(self.notification_object)
        logger.debug('Loaded %d notification service(s).', self.loaded_services)

    def info(self, body, title='Info'):
        """
        Sending a notification to the configured service(s) with the blue INFO notify_type.

        :param body: The message you want to send in the notification.
        :type body: str
        :param title: The title added the notification.
        :type title: str
        """
        if self.loaded_services >= 1 and self.notify_level <= 10:
            self.notification_object.notify(
                body=body,
                title=title,
                notify_type=NotifyType.INFO,
            )

    def success(self, body, title='Success'):
        """
        Sending a notification to the configured service(s) with the green SUCCESS notify_type.

        :param body: The message you want to send in the notification.
        :type body: str
        :param title: The title added the notification.
        :type title: str
        """
        if self.loaded_services >= 1 and self.notify_level <= 20:
            self.notification_object.notify(
                body=body,
                title=title,
                notify_type=NotifyType.SUCCESS,
            )

    def warning(self, body, title='Warning'):
        """
        Sending a notification to the configured service(s) with the yellow WARNING notify_type.

        :param body: The message you want to send in the notification.
        :type body: str
        :param title: The title added the notification.
        :type title: str
        """
        if self.loaded_services >= 1 and self.notify_level <= 30:
            self.notification_object.notify(
                body=body,
                title=title,
                notify_type=NotifyType.WARNING,
            )

    def failure(self, body, title='Failure'):
        """
        Sending a notification to the configured service(s) with the red FAILURE notify_type.

        :param body: The message you want to send in the notification.
        :type body: str
        :param title: The title added the notification.
        :type title: str
        """
        if self.loaded_services >= 1 and self.notify_level <= 40:
            self.notification_object.notify(
                body=body,
                title=title,
                notify_type=NotifyType.FAILURE,
            )
