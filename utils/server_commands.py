"""
This file holds all commands that the application can run on the server.
"""
import subprocess
from .logger import logging
from .notifications import Notifications


def run_command(command, working_directory, redirect_output=False):
    """
    Runs a command in the shell on the server in the pre-defined directory.

    :param command: The command we want to run in the shell.
    :type command: list
    :param working_directory: The directory where we run the command.
    :type working_directory: str
    :return: An error if an esception is thrown.
    :rtype: str
    """

    # Store the logger attribute
    logger = logging.logger
    # Initiate notifications
    notify = Notifications()

    # Variable command converted to string and nicely formatted
    command_formatted = ' '.join(command)

    logger.info('Running command on server: %s', command)
    notify.info(f'*Running command:* {command_formatted}')

    # Trying to perform the provided command
    try:
        if redirect_output is False:
            result = subprocess.run(
                command,
                cwd=working_directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
        else:
            result = subprocess.run(
                command,
                cwd=working_directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=True,
                timeout=300
            )

        logger.debug('stdout: %s', result.stdout)
        logger.info('%s was restarted.', working_directory)
        notify.success(f'*Successfully ran:* {command_formatted}')
        return result.stdout

    except subprocess.CalledProcessError as error:
        # Defining error message
        error_msg = f'CalledProcessError occurred while running {command} in {working_directory}.'
        if error.stderr is None:
            logger.critical(error_msg + f'Error: {error.stdout}')
            notify.failure(f'{error_msg} Error: {error.stdout}')
        else:
            logger.critical(error_msg + f'Error: {error.stderr}')
            notify.failure(f'{error_msg} Error: {error.stderr}')
        return error.stderr
    except subprocess.TimeoutExpired as error:
        # Defining error message
        error_msg = f'A timeout occurred while running {command} in {working_directory}.'
        if error.stderr is None:
            logger.critical(error_msg + f'Error: {error.stdout}')
            notify.failure(f'{error_msg} Error: {error.stdout}')
        else:
            logger.critical(error_msg + f'Error: {error.stderr}')
            notify.failure(f'{error_msg} Error: {error.stderr}')
        return error.stderr
    except OSError as error:
        error_msg = (
            f'An OSError occured while running {command} in {working_directory}. '
            f'Error: {error}'
        )
        logger.critical(error_msg)
        notify.failure(error_msg)
        return error
