""" Defines all global parameters and setting used by the web application.
This module should be imported like: import settings so that namespace conflicts are avoided.
"""

# Load environment variables
import os
import logging

# Load raspi only settings
if "arm" in os.uname()[4]:
    import board

    PIXEL_PIN = board.D12

else:
    PIXEL_PIN = None

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@{}:{}/{}'.format(
    os.getenv('MYSQL_USER', 'root'), os.getenv('MYSQL_PASSWORD', 'root'), os.getenv('MYSQL_HOST', '127.0.0.1'),
    os.getenv('MYSQL_PORT', '3306'), os.getenv('MYSQL_DATABASE', 'core_db_1'))

SQLALCHEMY_TRACK_MODIFICATIONS = False

# Global settings
LOG_LEVEL = logging.DEBUG

# Operating system variables
MAC_VERSION = {"Darwin"}

# Message variables
MAX_MESSAGE_SIZE = 4294967295  # Message size is stored in 4 bytes, so max is quite large ~4 billion

COMMAND_NAME = "command"
COMMAND_POSITIONAL_ARGUMENTS = "args"
COMMAND_KEYWORD_ARGUMENTS = "kwargs"
COMMAND_ENCODING = 'utf-8'

# Daemon variables
DAEMON_NAME = "neopixeld"
DAEMON_PID_FILE_PATH = f"/var/run/{DAEMON_NAME}.pid"
DAEMON_WORKING_DIRECTORY = f"/var/lib/{DAEMON_NAME}"

# Named pipe variables
STDIN_NAMED_PIPE_PATH = os.path.join(os.getcwd(), f"{DAEMON_NAME}.stdin")
STDOUT_NAMED_PIPE_PATH = os.path.join(os.getcwd(),f"{DAEMON_NAME}.stdout")

# Neopixel settings
MAX_NUM_PIXELS = 36

