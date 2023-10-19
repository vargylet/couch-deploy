"""
Small API that picks up a webhook from Github and processes the data to update
the local repository on the server.
"""
import logging
from logging.handlers import RotatingFileHandler
import json
import subprocess
import hmac
import hashlib
import threading
from flask import Flask, request

app = Flask(__name__)

# Creating logger for the app
logger = logging.getLogger("__name__")

# Set log level for opening the config file
logger.setLevel("INFO")

# Adding file handler to write the logs to file
LOG_FILE = "couch-deploy.log"
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=10240, backupCount=5)

# Defining the formatting of the logging
log_format = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
)
file_handler.setFormatter(log_format)

# Adding file handler to logger
logger.addHandler(file_handler)

# Reading the configuration file
try:
    with open("config.json", "r", encoding="utf-8)") as config_file:
        config = json.load(config_file)
    logger.info("The config file was loaded successfully")
except FileNotFoundError:
    logger.error("The config file could not be found")
except PermissionError:
    logger.error("The config file doesn't have the right permissions")
except IOError:
    logger.error("An I/O error occurred while trying to open the config file")

# Set log level based on config file
log_level = config.get("log_level", config["log_level"])
logger.setLevel(log_level)

def validate_signature(data, github_signature):
    """
    Generates the signature using the secret key. Then compares that signature
    with the incoming signature.

    :param data: The data we're receiving from the incoming webhook.
    :type data: json
    :param github_signature: The sha-256 signature received by GitHub.
    :type github_signature: str
    :return: True or false
    :rtype: bool
    """

    # Generate the signature with the secret
    expected_signature = "sha256=" + hmac.new(
        config["webhook_secret"].encode("utf-8"),
        data,
        hashlib.sha256
    ).hexdigest()

    logger.debug(
        "Validating incoming signature. Expected signature: %s - Incoming signature: %s",
        expected_signature,
        github_signature
    )

    # Comparing the generated signature with the received signature
    return hmac.compare_digest(expected_signature, github_signature)

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

    def log_critical(command, working_directory, error):
        """
        A nested function to log critical messages.

        :param command: The command that the script tried to run in the shell.
        :type command: str
        :param working_directory: The directory where the script tried to run the command.
        :type working_directory: str
        :return: An error message containing an error message.
        :rtype: str
        """
        logger.critical(
            "An error occured when running %s in %s. Error message: %s",
            command, working_directory, error
        )

    logger.info("Running command on server: %s", command)
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
                timeout=60
            )

        logger.debug("stdout: %s", result.stdout)
        return result.stdout

    except subprocess.CalledProcessError as error:
        log_critical(str(command), working_directory, error.stderr)
        return error.stderr
    except subprocess.TimeoutExpired as error:
        log_critical(str(command), working_directory, error.stderr)
        return error.stderr
    except OSError as error:
        log_critical(str(command), working_directory, "OSError")
        return "OSError"

logger.info("The app started successfully. Waiting for signals...")

@app.route(f"/{config['path']}", methods=["POST"])
def api_endpoint():
    """
    Receives the json data with the changes from git and updates
    the local repository on the server.

    :return: A HTML respons, either 200 or an error code.
    :rtype: str
    """

    # The data from GitHub
    raw_data = request.data

    # Get the request signature and payload
    github_signature = request.headers.get("X-Hub-Signature-256")

    # Verifying that the signature is not empty or didn't match
    if github_signature is None or not validate_signature(raw_data, github_signature):
        logger.warning("Authentication failed from %s", request.remote_addr)

        return "Authentication failed", 400

    data = json.loads(raw_data)
    local_path = config["local_path"]
    repository_name = data['repository']['name']

    if "commits" in data:
        # Verifying that "commits" is present in the received data
        # Looping the commits in the response
        for commit in data["commits"]:

            logger.debug("Taking action on %s", commit)

            # Looping the modified files in the commit
            for modified_file in commit["modified"]:

                logger.info("Processing %s", modified_file)

                # Splitting the string of the modified file
                modified_file_split = modified_file.rsplit("/", 1)
                if len(modified_file_split) >= 2:
                    docker_folder = modified_file_split[0]
                    docker_file = modified_file_split[1]
                else:
                    docker_file = modified_file_split[0]
                    docker_folder = f"No folder ({docker_file})"

                logger.debug("Docker file: %s. Docker folder: %s", docker_file, docker_folder)

                if docker_folder not in config["folders_to_trigger_on"]:
                    # If the changed folder isn't configured on this server
                    logger.info(
                        "The container is not configured on this server: %s", docker_folder
                    )
                    continue

                if docker_file != "docker-compose.yml":
                    # If the file in the commit isn't a docker compose file, we're stopping
                    logger.info(
                        "The updated file isn't a docker-compose.yml file: %s", docker_folder
                    )
                    continue

                # Pull from the repository
                run_command(
                    ["git", "pull", "--rebase"],
                    f"{local_path}/{repository_name}"
                )

                # Restart the docker container and recreate it as a background process
                docker_restart_thread = threading.Thread(
                        target=run_command,
                        args=(
                            ["docker", "compose", "up", "-d", "--force-recreate"],
                            f"{local_path}/{repository_name}/{docker_folder}",
                            True
                        ),
                    )

                try:
                    docker_restart_thread.start()
                except (subprocess.CalledProcessError) as error:
                    logger.critical("The command failed with a non-zero error: %s", error)
                except subprocess.TimeoutExpired as error:
                    logger.critical("The process timed out: %s", error)
                except OSError as error:
                    logger.critical("An OSError occured: %s", error)

    else:
        logger.info("The response didn't hold any data to process")

    logger.info("Successful run")

    return "Success", 200

if __name__ == "__main__":
    app.run()
