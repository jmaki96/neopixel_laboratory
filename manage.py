""" Management script for launching, testing, and migrating app.
"""
# pylint:disable=unused-argument,redefined-outer-name,broad-except

import logging
import time
import argparse
import datetime
import os
import subprocess
import shlex
import sys
import traceback

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

# manage.py settings
MYSQL_DATABASE_NAME = os.getenv('MYSQL_DATABASE', 'core_db_1')
MYSQL_USERNAME = os.getenv('MYSQL_USER', 'web_user')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password')
APP_MODULE_LOCATION = os.path.abspath(__file__).replace(__file__, "app")
SETUP_CONFIG_FILE_LOCATION = os.path.abspath(__file__).replace(__file__, "setup.cfg")

# docker compose files
YAML_CORE = 'core.yml'
YAML_DEV = 'dev.yml'

DOCKER_COMPOSE_PREFIX = f'docker compose -f {YAML_CORE}'

# container names
MY_SQL_DB_CONTAINER_NAME = "core_db_1"
CORE_WEB_APP_CONTAINER_NAME = "core_web_1"


# Logging helpers
def _log(message: str, verbose: bool, log_level: int = logging.INFO) -> None:
    """ Helper for logging messages based on verbosity
    Args:
        message (str): Message to log
        verbose (bool): Whether or not to log
        log_level (int, optional): What log level to use, defaults to Info
    """

    if verbose:
        if log_level == logging.DEBUG:  # TODO: Must be a more elegant solution here
            _logger.debug(message)
        elif log_level == logging.INFO:
            _logger.info(message)
        elif log_level == logging.WARNING:
            _logger.warning(message)
        elif log_level == logging.ERROR:
            _logger.error(message)
        elif log_level == logging.CRITICAL:
            _logger.critical(message)
        else:
            _logger.debug(message)  # Default to debug


# Command Helpers
def _check_call(command, show_stdout=True, show_stderr=True, debug=True) -> None:
    """ Wrapper around the subprocess check_call method

    Args:
        command ([type]): CLI command to execute on the bash shell
        show_stdout (bool, optional): Whether to print messages to stdout. Defaults to True.
        show_stderr (bool, optional): Whether to print messages to stderror. Defaults to True.
        debug (bool, optional): Whether to echo command into debug logger. Defaults to True.
    """

    if debug:
        _logger.debug("DEBUG: {0}".format(command))

    with open(os.devnull, 'w') as devnull:
        stdout = sys.stdout if show_stdout else devnull  # Pipe to devnull if False
        stderr = sys.stderr if show_stderr else devnull  # Pipe to devnull if False
        # shlex is used here to split the string command into the properly delimited array that
        # bash expects
        subprocess.check_call(shlex.split(command), stdout=stdout, stderr=stderr)


def _popen(command: str, show_stdout=True, show_stderr=True, debug=True, cwd=None) -> subprocess.Popen:
    """ Like _check_call wrapper, used to provide extension in the future

    Args:
        command (str): Command to execute in subprocess
        show_stdout (bool, optional): Whether to print messages to stdout. Defaults to True.
        show_stderr (bool, optional): Whether to print messages to stderror. Defaults to True.
        debug (bool, optional): Whether to echo command into debug logger. Defaults to True.
        cwd ([type], optional): Working directory to execute command in. Defaults to None.

    Returns:
        subprocess.Popen: [description]
    """

    if debug:
        _logger.debug('DEBUG: {}'.format(command))

    with open(os.devnull, 'w') as devnull:
        stdout = sys.stdout if show_stdout else devnull  # Pipe to devnull if False
        stderr = sys.stderr if show_stderr else devnull  # Pipe to devnull if False
        proc = subprocess.Popen(shlex.split(command), stdout=stdout, stderr=stderr, cwd=cwd)

        return proc


# Process Helprs
def _wait_for_mysql(container_name: str, verbose: bool = False) -> None:
    """ Blocking call, which waits for the mysql process in the named container to be ready.
    Args:
        container_name (str): The name of the Docker container where the mysql process should be running
        verbose (bool, optional): Whether to print messages. Defaults to False
    Raises:
        Exception: Raises an error if the mysql db in the container never responds appropriately
    """
    # pylint:disable=invalid-name

    mysql_ready = False
    timer = 30
    while not mysql_ready and timer > 0:
        time.sleep(1)
        timer -= 1
        rc = _popen(
            f'docker container exec {container_name} mysql '
            f'-u{MYSQL_USERNAME} -p{MYSQL_PASSWORD} -h127.0.0.1 {MYSQL_DATABASE_NAME} '
            '-e "show tables;"',
            show_stderr=verbose,
            show_stdout=verbose
        ).wait()
        mysql_ready = (rc == 0)
    if timer == 0:
        raise Exception('DB not initialized')


# CLI Commands
def run(args: argparse.Namespace) -> None:
    """ Properly initializes all of the necessary Docker containers for the web app and database to run successfully.
    Args:
        args (argparse.Namespace): CLI arguments passed in
    """

    _popen(
        DOCKER_COMPOSE_PREFIX + f' -f {YAML_DEV} start'
    ).wait()


def stop(args: argparse.Namespace) -> None:
    """ Stops any currently running Docker containers related to the web app
    Args:
        args (argparse.Namespace): CLI arguments passed in
    """

    _popen(
        DOCKER_COMPOSE_PREFIX + ' stop'
    ).wait()


def up(args: argparse.Namespace) -> None:
    """ Brings up Docker containers
    Args:
        args (argparse.Namespace): CLI arguments passed in
    """
    # pylint:disable=invalid-name

    _popen(
        DOCKER_COMPOSE_PREFIX + ' up -d --build --force-recreate'
    ).wait()


def down(args: argparse.Namespace) -> None:
    """ Brings down Docker containers
    Args:
        args (argparse.Namespace): CLI arguments passed in
    """

    _popen(
        DOCKER_COMPOSE_PREFIX + ' down'
    ).wait()


def shell(args: argparse.Namespace) -> None:
    """ Starts a shell session on the web app container, if it is running
    Args:
        args (argparse.Namespace): CLI arguments passed in
    """

    _popen(f'docker exec -it {args.container_name} bash').wait()


def test(args: argparse.Namespace) -> None:
    """ Manages all of the testing required for this project.
        Linting settings are kept in setup.cfg file
    Args:
        args (argparse.Namespace): CLI arguments passed in
    """

    # Switches for what linter to run, maybe should be parameterized
    run_flake8 = True
    run_mypy = True
    run_pylint = True

    if args.linting:
        # Only run code-style checks

        if run_flake8:
            # Running Flake8 checks
            # flake8 CLI docs: https://flake8.pycqa.org/en/latest/user/options.html#
            flake8_command = f'flake8 "{APP_MODULE_LOCATION}"'

            _logger.info(f"running flake8 command: {flake8_command}")
            _popen(flake8_command).wait()

        if run_mypy:
            # Running mypy checks
            # mypy CLI docs: https://mypy.readthedocs.io/en/stable/command_line.html
            mypy_command = f'mypy "{APP_MODULE_LOCATION}"'

            _logger.info(f"running mypy command: {mypy_command}")
            _popen(mypy_command).wait()

        if run_pylint:
            # Running pylint checks
            pylint_command = f'pylint "{APP_MODULE_LOCATION}"'

            _logger.info(f"running pylint command: {pylint_command}")
            _popen(pylint_command).wait()
    else:
        raise NotImplementedError("CURRENTLY ONLY LINTING CHECKS ARE IMPLEMENTED!")


if __name__ == "__main__":
    start_time = time.time()

    # ==============================
    # === MASTER ARGUMENT PARSER ===
    # ==============================
    # Master parser and global switches
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--verbose', action='store_true', help='Whether to verbosely print')

    # Initialize sub-commands
    subparsers = parser.add_subparsers()

    # ==================
    # === UP COMMAND ===
    # ==================
    up_parser = subparsers.add_parser('up', help='Brings up all relevant docker images for use.')
    up_parser.set_defaults(cmd=up)  # Register function to handle this command

    # ====================
    # === DOWN COMMAND ===
    # ====================
    down_parser = subparsers.add_parser('down', help='rings down all docker containers.')
    down_parser.set_defaults(cmd=down)  # Register function to handle this command

    # ===================
    # === RUN COMMAND ===
    # ===================
    run_parser = subparsers.add_parser('run', help='Start all relevant Docker containers.')
    run_parser.set_defaults(cmd=run)  # Register function to handle this command

    # ====================
    # === STOP COMMAND ===
    # ====================
    stop_parser = subparsers.add_parser('stop', help='Stops all the containers etc.')
    stop_parser.set_defaults(cmd=stop)  # Register function to handle this command

    # =====================
    # === SHELL COMMAND ===
    # =====================
    shell_parser = subparsers.add_parser('shell', help='Launches a shell session within one of the containers.')
    shell_parser.add_argument('-c', '--container_name', help='Name of the container to launch shell session in',
                              default=CORE_WEB_APP_CONTAINER_NAME)
    shell_parser.set_defaults(cmd=shell)  # Register function to handle this command

    # =======================
    # === TESTING COMMAND ===
    # =======================
    testing_parser = subparsers.add_parser('test',
                                           help='Manages running tests for style, logic, unit, and integration tests.')
    testing_parser.add_argument('-l', '--linting', action='store_true', help='Just run code-style (linting) tests.')
    testing_parser.set_defaults(cmd=test)  # Register function to handle this command

    DEBUGGING = True  # Maybe turn this into an argument
    if DEBUGGING:
        DOCKER_COMPOSE_PREFIX += f" -f {YAML_DEV}"

    try:
        args = parser.parse_args()

        if 'cmd' in args:
            args.cmd(args)  # Call function that is registered with command sub-parser
        else:
            parser.print_help(sys.stderr)
            sys.exit(1)

    except Exception:
        traceback.print_exc()
        parser.print_help(sys.stderr)
        sys.exit(1)

    end_time = time.time()
    _logger.info("manage.py finished in {0:.2f}s".format(end_time-start_time))
