"""
This module initializes the src package.
"""

# app package
from .config import settings
from .database import DataBase

__all__ = [
    'settings',
    'DataBase'
]

"""
NoteApp Backend Package
""" 