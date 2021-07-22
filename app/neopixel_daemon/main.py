""" Main entry-point script for the while True loop that manages the Neopixels.

The webservice should call this as a subprocess, because this script will run as a blocking process.
Basically, it's meant to run as a daemon-like service.

It should handle a TERM or KILL signal to exit gracefully.
"""

import os
import logging
import datetime

# =====================
# === LOGGING SETUP ===
# =====================

LOG_FORMAT = "%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s"
formatter = logging.Formatter(LOG_FORMAT)
_logger = logging.getLogger()
_logger.setLevel(logging.DEBUG)

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
