"""
Authentication of the incoming GitHub webhook.
"""
import hmac
import hashlib
from .config_loader import config_loader
from .logger import logger

# Store the config attribute
config = config_loader.config
# Store the logger attribute
logger = logger.logger


def github_signature(data, signature):
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
    expected_signature = 'sha256=' + hmac.new(
        config['webhook_secret'].encode('utf-8'),
        data,
        hashlib.sha256
    ).hexdigest()

    logger.debug(
        'Validating incoming signature. Expected signature: %s - Incoming signature: %s',
        expected_signature,
        signature
    )

    # Comparing the generated signature with the received signature
    return hmac.compare_digest(expected_signature, signature)
