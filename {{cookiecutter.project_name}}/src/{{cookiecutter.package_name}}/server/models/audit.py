"""Auditing types for Fastapipostgres - Fastapipostgres.

Copyright (C) 2023  Parker Wahle

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""  # noqa: E501, B950
from __future__ import annotations

import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field
from sqlmodel import SQLModel


class AuditEventType(Enum):
    """Types of audit events."""

    STARTUP = "startup"
    SHUTDOWN = "shutdown"
    OTHER = "other"


class AuditEvent(SQLModel, table=True):
    """A logged audit event that has occured in the system."""

    id: int = Field(default=None, primary_key=True)
    # SQLAlchemy and therefore SQLModel doesn't do timezone-aware datetimes very well,
    # so we strictly store timezone-naive datetimes in UTC and convert to local time
    # as needed.
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    event_user: Optional[str] = Field(None)
    event_type: AuditEventType = Field()
    event_data: Optional[bytes] = Field(None)  # messagepack data


__all__ = ("AuditEvent", "AuditEventType")
