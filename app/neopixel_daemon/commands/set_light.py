""" Command that powers off neopixels
"""
import logging
from typing import Tuple

import neopixel

from settings import PIXEL_PIN, MAX_NUM_PIXELS
from commands.command import Command

_logger = logging.getLogger(__name__)

class SetLightCommand(Command):
    """ Powers off neopixels."""

    @classmethod
    def command_name(cls) -> str:
        return "set"
    
    def execute(self) -> None:
        brightness = float(self.kwargs["brightness"])
        color = self._get_color(self.kwargs["color"])

        _logger.debug(f"programming neopixels with brightness: {brightness} and color: {color}")
        pixels = neopixel.NeoPixel(PIXEL_PIN, MAX_NUM_PIXELS, brightness=brightness, auto_write=False)

        pixels.fill(color)
        pixels.show()

    def _get_color(self, color: str) -> Tuple[int, int, int]:
        """ Parses RGB color values from string. 

        Expects color string to be of the format
            Hex: 0xFFFFFF  (first byte is red, second byte is green, third byte is blue)
            Dec: 255-255-255 

        Args:
            color (str): string encoding color values

        Returns:
            Tuple[int, int, int]: Tuple of 3 integers (red, green, blue)
        """

        if color[:2] == "0x":
            # Hex
            r = int("0x" + color[2:4])
            g = int("0x" + color[4:6])
            b = int("0x" + color[6:8])
        elif "-" in color:
            # Dec
            r, g, b, = [int(val) for val in color.split("-")]
        else:
            raise ValueError(f"Cannot parse color from string: {color}")
        
        return (r, g, b)