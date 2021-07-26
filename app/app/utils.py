""" Shared utility functions across application
"""

import os


def is_raspi() -> bool:
    """ Checks if the current OS is raspi
    
    Returns:
        bool True if raspi, False else
    """

    if "uname" in os.__dict__:
        if "arm" in os.uname()[4]:
            return True
    
    return False
