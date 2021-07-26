""" Main entry-point for the Flask app to be initialized and called from
"""

import os
import logging
import datetime

from flask import Flask

from app.extensions.flask_database import db
from app.test.routes import bp as test_bp
from app.neopixel.routes import bp as np_bp
from app import settings

# =====================
# === LOGGING SETUP ===
# =====================

LOG_FORMAT = "%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s"
formatter = logging.Formatter(LOG_FORMAT)
_logger = logging.getLogger()
_logger.setLevel(settings.LOG_LEVEL)

datestamp = datetime.datetime.now().strftime("%m%d%Y_%H%M%S")

# console logging
CONSOLE_LOGGING = True
if CONSOLE_LOGGING:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)

# file logging
FILE_LOGGING = True
log_directory = os.path.join(os.getcwd(), "logs")
if FILE_LOGGING:
    if not os.path.exists(log_directory):
        os.mkdir(log_directory)

    debug_log_handler = logging.FileHandler(os.path.join(log_directory, "debug_{0}.log".format(datestamp)))
    debug_log_handler.setLevel(logging.DEBUG)
    debug_log_handler.setFormatter(formatter)
    _logger.addHandler(debug_log_handler)

# Log level test
_logger.info("INFO")
_logger.debug("DEBUG")

# ==================================
# === FLASK APPLICATION CREATION ===
# ==================================

_logger.info("Creating flask application...")
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    SQLALCHEMY_DATABASE_URI=settings.SQLALCHEMY_DATABASE_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS=settings.SQLALCHEMY_TRACK_MODIFICATIONS
)
_logger.info("Done.")

# ===============================
# === DATABASE INITIALIZATION ===
# ===============================

_logger.info("Initializing MySQL database connection...")
db.init_app(app)
_logger.info("Done.")

# ==========================
# === CLI INITIALIZATION ===
# ===========================

_logger.info("Initializing Flask CLI commands...")
_logger.info("Done.")

# ===========================
# === REGISTER BLUEPRINTS ===
# ===========================

_logger.info("Registering Flask blueprints...")
app.register_blueprint(test_bp)
app.register_blueprint(np_bp)
_logger.info("Done.")


if __name__ == "__main__":
    app.run()