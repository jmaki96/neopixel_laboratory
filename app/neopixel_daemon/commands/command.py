""" Abstract base class for Command
"""

import logging
from abc import abstractmethod, ABC
from typing import Any, List, Dict

from settings import COMMAND_NAME, COMMAND_KEYWORD_ARGUMENTS, COMMAND_POSITIONAL_ARGUMENTS

_logger = logging.getLogger(__name__)


class Command(ABC):
    """ Abstract base class for any command that the neopixel daemon can execute.
    """

    commands = {}

    def __init__(self, args: List[str], kwargs: Dict[str, str]):
        
        # Initialize arguments
        self.args = args
        self.kwargs = kwargs

        super(Command, self).__init__()

        _logger.debug(f"finished constructing: {self.__class__} instance")

    @abstractmethod
    def execute(self) -> None:
        """ Executes command with initialized args and kwargs."""

        raise NotImplementedError("Child class must implemented this method")

    @classmethod
    @abstractmethod
    def command_name(cls) -> str:
        """ Returns the command name, as expected in the command message.

        Returns:
            str: command name
        """

        raise NotImplementedError("Child class must implemented this method")

    @classmethod
    def build_command(cls, command: Dict[str, Any]) -> 'Command':
        """ Factory method. Constructs appropriate command subclass for this command type.

        Args:
            command (Dict[str, Any]): Should contain command_name (str), command_args (List[str]), and command_kwargs (Dict[str, str])
        
        Returns:
            Command: Command object
        
        Raises:
            ValueError: If the command name cannot be found
        """

        _logger.debug("build_command called.")

        command_name = command[COMMAND_NAME]
        command_args = command[COMMAND_POSITIONAL_ARGUMENTS]
        command_kwargs = command[COMMAND_KEYWORD_ARGUMENTS]

        _logger.debug("Received: {} {} {}".format(command_name,
                                                 " ".join(command_args),
                                                 " ".join([f"-{k} {v}" for k, v in command_kwargs.items()])))

        for subclass in cls.__subclasses__():
            _logger.debug(f"trying subclass {subclass}...")

            _logger.debug(f"subclass has name: {subclass.command_name()}")
            if subclass.command_name() == command_name:
                return subclass(command_args, command_kwargs)
        else:
            raise ValueError(f"Cannot find command named: {command_name}")

# Register commands
from commands.off_command import OffCommand
from commands.set_light import SetLightCommand

class EchoCommand(Command):
    """ Testing command which simply echoes back the name, args, and kwargs."""

    @classmethod
    def command_name(cls) -> str:
        return "echo"
    
    def execute(self) -> None:
        """ Echoes name, args, and kwargs.
        """
        _logger.debug("Echo command called.")
        _logger.info("{} {} {}".format(self.__class__.command_name(),
                                       " ".join(self.args),
                                       " ".join([f"-{k} {v}" for k, v in self.kwargs.items()])))
