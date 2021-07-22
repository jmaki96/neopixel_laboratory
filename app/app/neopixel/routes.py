""" URLs for sending requests and starting Neopixl daemon
"""

import logging

from flask import Blueprint, Response, make_response

_logger = logging.getLogger(__name__)

bp = Blueprint('neopixel', __name__, url_prefix='/np')


@bp.route('/start', methods=["GET"])
def hello() -> Response:
    """ Start running the Neopixel daemon. Optionally, provide an RGB hex code. 

    Returns:
        Response: HTTP OK Response with content Hello, World!
    """


    return make_response("Hello, world!", 200)