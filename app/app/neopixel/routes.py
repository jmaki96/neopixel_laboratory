""" URLs for sending requests and starting Neopixl daemon
"""

import logging

from flask import Blueprint, Response, make_response, request

from app.messaging import write_command
from app.settings import STDIN_NAMED_PIPE_PATH

_logger = logging.getLogger(__name__)

bp = Blueprint('neopixel', __name__, url_prefix='/np')


@bp.route('/submit_command')
def submit_command() -> Response:
    """ Submits a command to the neopixeld, and returns its response.

    Returns:
        Response: [description]
    """

    command_name = request.args.get("command_name", "")
    command_args = request.args.get("command_args", [])
    command_kwargs = request.args.get("command_kwargs", {})

    write_command(command_name, command_args, command_kwargs, fifo=STDIN_NAMED_PIPE_PATH)

    return make_response("", 200)


@bp.route('/start', methods=["GET"])
def hello() -> Response:
    """ Start running the Neopixel daemon. Optionally, provide an RGB hex code. 

    Returns:
        Response: HTTP OK Response with content Hello, World!
    """


    return make_response("Hello, world!", 200)