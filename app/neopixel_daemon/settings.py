""" Stores global settings for neopixeld
"""
import os
import board

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
PIXEL_PIN = board.D12
MAX_NUM_PIXELS = 36
