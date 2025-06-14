# Database package for ATS CV Search Application
"""
This package contains database configuration, models, and repository classes
for the ATS CV Search application.
"""

from .config_simple import DatabaseConfig
from .repo import ResumeRepository

__all__ = ['DatabaseConfig', 'ResumeRepository']