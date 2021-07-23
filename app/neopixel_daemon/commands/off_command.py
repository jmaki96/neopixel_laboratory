""" Command that powers off neopixels
"""
import neopixel

from settings import PIXEL_PIN, MAX_NUM_PIXELS
from commands.command import Command


class OffCommand(Command):
    """ Powers off neopixels."""

    @classmethod
    def command_name(cls) -> str:
        return "off"
    
    def execute(self) -> None:
        pixels = neopixel.NeoPixel(PIXEL_PIN, MAX_NUM_PIXELS)
        pixels.fill((0, 0, 0))
