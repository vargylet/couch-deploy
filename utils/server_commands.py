"""
This file holds all commands that the application can run on the server.
"""
import subprocess
# from app import logger
from .config_logger import config_logger


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

    # Initiate the logger
    logger = config_logger.logger

    logger.info('Running command on server: %s', command)
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
        return result.stdout

    except subprocess.CalledProcessError as error:
        # Defining error message
        error_msg = f'CalledProcessError occurred while running {command} in {working_directory}.'
        if error.stderr is None:
            logger.critical(error_msg + f'Error: {error.stdout}')
        else:
            logger.critical(error_msg + f'Error: {error.stderr}')
        return error.stderr
    except subprocess.TimeoutExpired as error:
        # Defining error message
        error_msg = f'A timeout occurred while running {command} in {working_directory}.'
        if error.stderr is None:
            logger.critical(error_msg + f'Error: {error.stdout}')
        else:
            logger.critical(error_msg + f'Error: {error.stderr}')
        return error.stderr
    except OSError as error:
        logger.critical(
            'An OSError occured while running %s in %s. Error: %s',
            command, working_directory, error
        )
        return error
