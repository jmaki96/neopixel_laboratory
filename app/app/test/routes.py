""" Simple test URLs for doing basic testing of the Flask app
"""

import logging

from flask import Blueprint, Response, make_response

_logger = logging.getLogger(__name__)

bp = Blueprint('test', __name__, url_prefix='/test')


@bp.route('/hello', methods=["GET"])
def hello() -> Response:
    """ Basic "Hello, World!" URL test.

    Returns:
        Response: HTTP OK Response with content Hello, World!
    """

    _logger.info("Received request to /test/hello!")

    return make_response("Hello, world!", 200)
