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
import signal
import json
import argparse
import subprocess
import shlex
import platform

import daemon
from daemon import pidfile

from settings import * 
from messaging import read_command
from commands.command import Command

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

    debug_fd = debug_log_handler.stream.fileno()

# Log level test
_logger.info("INFO")
_logger.debug("DEBUG")


def main():
    """ Main daemon process, which polls named pipe (i.e. stdin) for commands and responds
    """

    # Open up pipes 
    if not os.path.exists(STDOUT_NAMED_PIPE_PATH):
        os.mkfifo(STDOUT_NAMED_PIPE_PATH)
    
    if not os.path.exists(STDIN_NAMED_PIPE_PATH):
        os.mkfifo(STDIN_NAMED_PIPE_PATH)
    
    while True:
        _logger.debug("Waiting for command...")
        command = read_command()
        _logger.debug("Received: {} {} {}".format(command[COMMAND_NAME],
                                                 " ".join(command[COMMAND_POSITIONAL_ARGUMENTS]),
                                                 " ".join([f"-{k} {v}" for k, v in command[COMMAND_KEYWORD_ARGUMENTS].items()])))

        Command.build_command(command).execute()


def _interrupt() -> None:
    """ Handles SIGINT
    """

    _logger.debug("received SIGINT")

    exit(0)


def _terminate() -> None:
    """ Helper function, which handles SIGTERM
    """

    _logger.debug("received SIGTERM.")


def _hangup() -> None:
    """ Helper function, which handles SIGHUP
    """

    _logger.debug("received SIGHUP.")


def _has_admin_privileges() -> bool:
    """ Checks to see if the script is being run with sufficient privilege

    Returns:
        bool: True if user has appropriate privileges, else False
    
    Raises:
        ValueError: If it cannot determine admin privileges for this system
    """

    system_name = platform.system()

    if system_name in MAC_VERSION or system_name == "Linux":
        euid = os.getuid()
        _logger.debug(f"euid is {euid}")
        return euid == 0
    else:
        raise ValueError(f"Unknown system type {system_name}, cannot determine if admin privileges.")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-s', '--start', action='store_true', help='Start running daemon process. Error if already running.')
    parser.add_argument('-k', '--kill', action='store_true', help='Kill running daemon process if it exists. Does nothing otherwise. If called with -s, kill will resolve first.')
    args = parser.parse_args()

    if not _has_admin_privileges():
        raise PermissionError("Script must be run with root privileges or unexpected behavior may occur.")

    if args.kill:
        if os.path.exists(DAEMON_PID_FILE_PATH):
            with open(DAEMON_PID_FILE_PATH, "r") as pid_h:
                pid = int(pid_h.readline())

                subprocess.call(shlex.split(f"kill {pid}"))

    
    if args.start:
        _logger.info(f"Configuring daemon with pidfile: {DAEMON_PID_FILE_PATH}")

        uid = os.getuid()
        gid = os.getgid()

        _logger.info(f"Configuring daemon with uid: {uid} and gid: {gid}")

        if not os.path.exists(DAEMON_WORKING_DIRECTORY):
            _logger.info(f"Creating working directory at {DAEMON_WORKING_DIRECTORY}")
            os.makedirs(DAEMON_WORKING_DIRECTORY)
        
        # initialize daemon context
        context = daemon.DaemonContext(
            detach_process=True,
            files_preserve=[debug_fd],
            pidfile=pidfile.TimeoutPIDLockFile(DAEMON_PID_FILE_PATH),
            working_directory=DAEMON_WORKING_DIRECTORY,
            uid=uid,
            gid=gid
        )

        # Configure signal handlers
        context.signal_map = {
            signal.SIGTERM: _terminate,
            signal.SIGHUP: _hangup,
            signal.SIGINT: _interrupt
        }

        _logger.info("Launching daemon")
        with context:
            main()
