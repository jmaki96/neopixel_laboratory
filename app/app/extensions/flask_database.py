""" Define, configure, and declare SQLAlchemy database instance.
In the future, this could be used to define, declare, and instantiate an extension for SQLAlchemy.
"""
import logging

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

_logger = logging.getLogger(__name__)

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)
