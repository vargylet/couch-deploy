"""
All routes for the application.
"""
import json
import subprocess
import threading
from flask import request, Blueprint
from utils.config_loader import config_loader
from utils.logger import logger
from utils.authentication import github_signature
from utils.server_commands import run_command

# Store the config attribute
config = config_loader.config
# Store the logger attribute
logger = logger.logger

# Creating Blueprints for routes
api_endpoint = Blueprint('api_endpoint', __name__)


@api_endpoint.route(f'/{config["path"]}', methods=['POST'])
def api_endpoint_github():
    """
    Receives the json data with the changes from git and updates
    the local repository on the server.

    :return: A HTML respons, either 200 or an error code.
    :rtype: str
    """

    # The data from GitHub
    raw_data = request.data

    # Get the request signature and payload
    github_signature_data = request.headers.get('X-Hub-Signature-256')

    # Verifying that the signature is not empty or didn't match
    if github_signature_data is None or not github_signature(raw_data, github_signature_data):
        logger.warning('Authentication failed from %s', request.remote_addr)

        return 'Authentication failed', 400

    data = json.loads(raw_data)
    local_path = config['local_path']
    repository_name = data['repository']['name']

    if 'commits' in data:
        # Verifying that 'commits' is present in the received data
        # Looping the commits in the response
        for commit in data['commits']:

            logger.debug('Taking action on %s', commit)

            # Looping the modified files in the commit
            for modified_file in commit['modified']:

                logger.info('Processing %s', modified_file)

                # Splitting the string of the modified file
                modified_file_split = modified_file.rsplit('/', 1)
                if len(modified_file_split) >= 2:
                    docker_folder = modified_file_split[0]
                    docker_file = modified_file_split[1]
                else:
                    docker_file = modified_file_split[0]
                    docker_folder = f'No folder ({docker_file})'

                logger.debug('Docker file: %s. Docker folder: %s', docker_file, docker_folder)

                if docker_folder not in config['folders_to_trigger_on']:
                    # If the changed folder isn't configured on this server
                    logger.info(
                        'The container is not configured on this server: %s', docker_folder
                    )
                    continue

                if docker_file != 'docker-compose.yml':
                    # If the file in the commit isn't a docker compose file, we're stopping
                    logger.info(
                        'The updated file isn\'t a docker-compose.yml file: %s', docker_folder
                    )
                    continue

                # Pull from the repository
                run_command(
                    ['git', 'pull', '--rebase'],
                    f'{local_path}/{repository_name}'
                )

                # Restart the docker container and recreate it as a background process
                docker_restart_thread = threading.Thread(
                        target=run_command,
                        args=(
                            ['docker', 'compose', 'up', '-d', '--force-recreate'],
                            f'{local_path}/{repository_name}/{docker_folder}',
                            True
                        ),
                    )

                try:
                    docker_restart_thread.start()
                except (subprocess.CalledProcessError) as error:
                    logger.critical('The command failed with a non-zero error: %s', error)
                except subprocess.TimeoutExpired as error:
                    logger.critical('The process timed out: %s', error)
                except OSError as error:
                    logger.critical('An OSError occured: %s', error)

    else:
        logger.info('The response didn\'t hold any data to process')

    logger.info('Successful run')

    return 'Success', 200
