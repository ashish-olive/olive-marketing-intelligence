"""Shared data layer package"""
from .models import db
from .config import AppConfig

__all__ = ['db', 'AppConfig']
