""" Defines all global parameters and setting used by the web application.
This module should be imported like: import settings so that namespace conflicts are avoided.
"""

# Load environment variables
import os
import logging

import board

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@{}:{}/{}'.format(
    os.getenv('MYSQL_USER', 'root'), os.getenv('MYSQL_PASSWORD', 'root'), os.getenv('MYSQL_HOST', '127.0.0.1'),
    os.getenv('MYSQL_PORT', '3306'), os.getenv('MYSQL_DATABASE', 'core_db_1'))

SQLALCHEMY_TRACK_MODIFICATIONS = False

# Global settings
LOG_LEVEL = logging.DEBUG

# Neopixel settings
PIXEL_PIN = board.D12
MAX_NUM_PIXELS = 36
