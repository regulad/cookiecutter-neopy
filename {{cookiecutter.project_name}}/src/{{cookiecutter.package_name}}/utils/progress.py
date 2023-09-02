"""Progress tracking for Fastapipostgres - Fastapipostgres.

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

from io import StringIO

from rich.console import Console
from rich.progress import Progress


STUB_CONSOLE_IO = StringIO(initial_value="", newline="")
STUB_CONSOLE = Console(file=STUB_CONSOLE_IO, quiet=True)
STUB_PROGRESS = Progress(console=STUB_CONSOLE, auto_refresh=False, disable=True)

__all__ = ("STUB_CONSOLE", "STUB_PROGRESS", "STUB_CONSOLE_IO")
