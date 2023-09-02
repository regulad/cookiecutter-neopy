"""Utilities for Fastapipostgres - Fastapipostgres.

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

from datetime import datetime

import pytz


def timezone_aware_now(localized: bool = False) -> datetime:
    """Return a timezone-aware datetime object representing the current time."""
    utc_localized = pytz.UTC.localize(datetime.utcnow())
    return utc_localized if not localized else utc_localized.astimezone()


__all__ = ("timezone_aware_now",)
