"""FastAPI objects for Fastapipostgres - Fastapipostgres.

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

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from .._metadata import __summary__
from .._metadata import __title__
from .._metadata import __version__
from .routes.status import router as status_router


app = FastAPI(
    debug=__debug__,
    title=__title__,
    description=__summary__,
    version=__version__,
    default_response_class=ORJSONResponse,  # more performant than JSON
)

app.include_router(status_router, prefix="/status", tags=["status"])

__all__ = ("app",)
