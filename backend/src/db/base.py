"""
Base class for all SQLAlchemy models.

Provides common functionality and configuration for all database entities.
"""

from sqlalchemy.orm import declarative_base, DeclarativeBase
from sqlalchemy import MetaData

# Use the new declarative base from SQLAlchemy 2.x
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    def __repr__(self) -> str:
        """String representation of model instance."""
        columns = []
        for col in self.__table__.columns:
            value = getattr(self, col.name)
            columns.append(f"{col.name}={value!r}")
        return f"<{self.__class__.__name__}({', '.join(columns)})>"
