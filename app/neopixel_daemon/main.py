""" Main entry-point script for the while True loop that manages the Neopixels.

The webservice should call this as a subprocess, because this script will run as a blocking process.
Basically, it's meant to run as a daemon-like service.

It should handle a TERM or KILL signal to exit gracefully.

What should the Neopixel service do?
    - It should power off the Neopixel's gracefully on exit
    - It should support a power off command
    - It should support both a per LED, per ring and all LED command to program to a specific RGB and brightness
    - It should support an arbitrary set of pre-defined patterns, which should all consume a brightness setting
"""

import os
import logging
import datetime
import sys
import signal

import daemon

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

STDIN_NAMED_PIPE = "neopixeld.stdin"
STDOUT_NAMED_PIPE = "neopixeld.stdout"


def main():
    """ Main daemon process, which polls named pipe (i.e. stdin) for commands and responds
    """

    command = sys.stdin.readline()

    if "valid" in command:
        print(f"received valid command: {command}")
    else:
        print(f"received invalid command: {command}")


def _terminate() -> None:
    """ Helper function, which handles SIGTERM
    """

    print("received SIGTERM.")


def _hangup() -> None:
    """ Helper function, which handles SIGHUP
    """

    print("received SIGHUP.")


if __name__ == "__main__":

    # Instantiate named pipes
    stdout_named_pipe_path = os.path.join(os.getcwd(), STDOUT_NAMED_PIPE)
    stdin_named_pipe_path = os.path.join(os.getcwd(), STDIN_NAMED_PIPE)
    if not os.path.exists(stdout_named_pipe_path):
        os.mkfifo(stdout_named_pipe_path)
    
    if not os.path.exists(stdin_named_pipe_path):
        os.mkfifo(stdin_named_pipe_path)
    
    _logger.info("Opening named pipes...")
    with open(stdin_named_pipe_path, "r") as stdin_h, open(stdout_named_pipe_path, "w") as stdout_h:
        # initialize daemon context
        context = daemon.DaemonContext(
            stdin=stdin_h,
            stdout=stdout_h
        )

        # Configure signal handlers
        context.signal_map = {
            signal.SIGTERM: _terminate,
            signal.SIGHUP: _hangup
        }

        _logger.info("Launching daemon")
        with context:
            main()
    

        

