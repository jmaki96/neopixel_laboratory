""" URLs for sending requests and starting Neopixl daemon
"""

import logging

from flask import Blueprint, Response, make_response

_logger = logging.getLogger(__name__)

bp = Blueprint('neopixel', __name__, url_prefix='/np')


@bp.route('/submit_command')
def submit_command() -> Response:
    """ Submits a command to the neopixeld, and returns its response.

    Returns:
        Response: [description]
    """

    pass


@bp.route('/off')
def off() -> Response:
    """ Turns off all running neopixels

    Returns:
        Response: OK if process exits appropriately
    """

    return make_response("OK", 200)

@bp.route('/start', methods=["GET"])
def hello() -> Response:
    """ Start running the Neopixel daemon. Optionally, provide an RGB hex code. 

    Returns:
        Response: HTTP OK Response with content Hello, World!
    """


    return make_response("Hello, world!", 200)