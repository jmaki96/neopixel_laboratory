""" Module for encoding and decoding messages in named pipe queues.
"""

import struct
import json
import os
import logging
import sys
from typing import List, Dict, Optional

from app.settings import MAX_MESSAGE_SIZE, STDIN_NAMED_PIPE_PATH, STDOUT_NAMED_PIPE_PATH, \
                     COMMAND_NAME, COMMAND_KEYWORD_ARGUMENTS, COMMAND_POSITIONAL_ARGUMENTS, \
                     COMMAND_ENCODING

_logger = logging.getLogger()


def encode_msg_size(size: int) -> bytes:
    """ Encodes message size in bytes.

    Args:
        size (int): How many bytes in the message

    Returns:
        bytes: Size encoded in bytes
    """
    return struct.pack("<I", size)


def decode_msg_size(size_bytes: bytes) -> int:
    """ Consumes a set of bytes that represent how many bytes are in the message 

    Args:
        size_bytes (bytes): Bytes that represent the size of the message

    Returns:
        int: How many bytes are in the subsequent message
    """
    return struct.unpack("<I", size_bytes)[0]


def create_msg(content: bytes) -> bytes:
    """ Creates message by encoding size as 4 bytes at the beginning of the message

    Args:
        content (bytes): Message contents in bytes

    Raises:
        ValueError: If (somehow) the message is longer than the maximum

    Returns:
        bytes: Message with size bytes encoded
    """
    size = len(content)
    if size > MAX_MESSAGE_SIZE:
        raise ValueError(f"Message is too long. Maximum size in bytes is: {MAX_MESSAGE_SIZE}")
    return encode_msg_size(size) + content


def get_message(fifo: str) -> bytes:
    """ Retrieves message from named pipe.

    Args:
        fifo (str): fifo file path

    Returns:
        bytes: Message content bytes
    
    Raises:
        FileNotFoundError: If the named pipe has not been opened yet.
    """

    with open(fifo, "rb") as fifo_h:
        msg_size_bytes = fifo_h.read(4)
        msg_size = decode_msg_size(msg_size_bytes)
        msg_content = fifo_h.read(msg_size)

    return msg_content


def write_command(command: str, args: List[str], kwargs: Dict[str, str], fifo: Optional[str] = STDIN_NAMED_PIPE_PATH) -> None:
    """ Writes a command with arguments to STDIN queue.

    Args:
        command (str): command to issue
        args (List[str]): positional arguments in a list
        kwargs (Dict[str, str]): keyword arguments, after positional arguments
        fifo (str, optional): the name of the pipe to write too. Defaults to STDIN_NAMED_PIPE.
    
    Raises:
        FileNotFoundError: If the named pipe has not been opened yet.
    """

    command_schema = {
        COMMAND_NAME: command,
        COMMAND_POSITIONAL_ARGUMENTS: args,
        COMMAND_KEYWORD_ARGUMENTS: kwargs
    }

    command_byte_string = json.dumps(command_schema).encode(COMMAND_ENCODING)
    _logger.debug(f"command_byte_string: {command_byte_string}")

    with open(fifo, "wb") as stdout_h:
        message = create_msg(command_byte_string)
        stdout_h.write(message)
    

def read_command(timeout: Optional[float] = 30, fifo: Optional[str] = STDIN_NAMED_PIPE_PATH) -> Dict[str, str]:
    """ Reads the first command in the pipe.

    Args:
        timeout (float, optional): Time in seconds to wait before error. Defaults to 30s.
        fifo (str, optional): pipe to read from. Defaults to STDIN_NAMED_PIPE

    Returns:
        Dict[str, str]: Command read from pipe
    """

    # TODO: Implement timeout
    command_string = get_message(fifo).decode(COMMAND_ENCODING)

    command = json.loads(command_string)

    return command    


if __name__ == "__main__":

    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    if sys.argv[1] == "read":
        command = read_command(fifo=STDOUT_NAMED_PIPE_PATH)

        command_name_string = command[COMMAND_NAME]
        command_pos_args_string = " ".join(command[COMMAND_POSITIONAL_ARGUMENTS])
        command_key_args_string = " ".join([f"-{k} {v}" for k, v in command[COMMAND_KEYWORD_ARGUMENTS].items()])

        _logger.info(f"Read: {command_name_string} {command_pos_args_string} {command_key_args_string}")

    elif sys.argv[1] == "write":
        if not os.path.exists(STDIN_NAMED_PIPE_PATH):
            os.mkfifo(STDIN_NAMED_PIPE_PATH)

        if sys.argv[2] == "echo":
            write_command("echo", 
                        ["pos_arg1", "pos_arg2"], 
                        {"key1": "value1",
                        "key2": "value2"},
                        fifo=STDIN_NAMED_PIPE_PATH)
        elif sys.argv[2] == "off":
            write_command("off", 
                         [], 
                         {},
                         fifo=STDIN_NAMED_PIPE_PATH)
        elif sys.argv[2] == "set":
            write_command("set", 
                         [], 
                         {"brightness": "0.6",
                          "color": "0xE09D37"},
                         fifo=STDIN_NAMED_PIPE_PATH)
        else:
            _logger.info(f"Unknown command type {sys.argv[2]}")
    else:
        _logger.info(f"Unknown command {sys.argv[1]}")