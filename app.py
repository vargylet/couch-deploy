"""
Small API that picks up a webhook from Github and processes the data to update
the local repository on the server.
"""
import json
import subprocess
import hmac
import hashlib
import threading
from flask import Flask, request, jsonify

app = Flask(__name__)

# Reading the configuration file.
with open("config.json", "r", encoding="utf-8)") as config_file:
    config = json.load(config_file)

# Defining a dictionary to store the response
json_response = []

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

    # Comparing the generated signature with the received signature
    return hmac.compare_digest(expected_signature, github_signature)

def run_command(command, working_directory):
    """
    Runs a command in the shell on the server in the pre-defined directory.

    :param command: The command we want to run in the shell.
    :type command: list
    :param working_directory: The directory where we run the command.
    :type working_directory: str
    :return: An error if an esception is thrown.
    :rtype: str
    """
    try:
        result = subprocess.run(
            command,
            cwd=working_directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as error:
        error_message = (
            f"An error occured when running {command} in {working_directory}."
            f"Error message: {error.stderr} ({error.returncode})"
        )
        return error_message

def build_json_response(docker_folder, result_message):
    """
    Received information about what should go into the json output and appends it.

    :param docker_folder: The folder which has a change to it which will be passed to the output.
    :type docker_folder: str
    :param result_message: The message that will be passed to the output.
    :type result_message: str
    :return: A string formatted as JSON
    :rtype: json
    """
    response = {
        "folder": docker_folder,
        "result": result_message
    }

    # Append to the response list
    json_response.append(response)

@app.route(f"/{config['path']}", methods=["POST"])
def api_endpoint():
    """
    Receives the json data with the changes from git and updates
    the local repository on the server.

    :return: A HTML respons, either 200 or an error code.
    :rtype: str
    """

    # Reset the response data
    json_response.clear()

    # The data from GitHub
    raw_data = request.data

    # Get the request signature and payload
    github_signature = request.headers.get("X-Hub-Signature-256")

    if validate_signature(raw_data, github_signature):

        data = json.loads(raw_data)
        local_path = config["local_path"]
        repository_name = data['repository']['name']

        if "commits" in data:
            # Verifying that "commits" is present in the received data
            # Looping the commits in the response
            for commit in data["commits"]:

                # Looping the modified files in the commit
                for modified_file in commit["modified"]:

                    # Splitting the string of the modified file
                    modified_file_split = modified_file.rsplit("/", 1)
                    if len(modified_file_split) >= 2:
                        docker_folder = modified_file_split[0]
                        docker_file = modified_file_split[1]
                    else:
                        docker_file = modified_file_split[0]
                        docker_folder = f"No folder ({docker_file})"

                    if docker_folder not in config["folders_to_trigger_on"]:
                        # If the changed folder isn't configured on this server
                        build_json_response(
                            docker_folder,
                            "The container is not configured on this server.")
                        continue

                    if docker_file != "docker-compose.yml":
                        # If the file in the commit isn't a docker compose file, we're stopping
                        build_json_response(
                            docker_folder,
                            "The updated file wasn't a docker-compose.yml file.")
                        continue

                    # Pull from the repository
                    run_command(
                        ["git", "pull", "--rebase"],
                        f"{local_path}/{repository_name}"
                    )

                    # Restart the docker container as a background process and recreate
                    docker_restart_thread = threading.Thread(
                        target=run_command,
                        args=(["docker", "compose", "up", "-d", "--force-recreate"],
                        f"{local_path}/{repository_name}/{docker_folder}")
                    )
                    docker_restart_thread.start()

        build_json_response(
            "No folder (no data)",
            "The data provided couldn't be processed or was empty."
        )

        response = {
            "result": "success",
            "commits": json_response
        }
        return jsonify(response)

    # Returns a 403 with an error if auth fails
    response = {
            "result": "Authentication failed."
        }
    return jsonify(response), 403

if __name__ == "__main__":
    app.run()
