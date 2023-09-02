"""Profiling for Fastapipostgres - Fastapipostgres.

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

from contextlib import contextmanager
from typing import Generator
from typing import TypeAlias

from rich.progress import Progress

from .progress import STUB_PROGRESS


PYTHON_PROFILER: bool
try:
    import cProfile as profile  # noqa: N813

    PYTHON_PROFILER = False
except ImportError:  # pragma: no cover
    import profile  # type: ignore

    PYTHON_PROFILER = True

PROFILER_TYPE: TypeAlias = profile.Profile


@contextmanager
def prepare_profiler(
    progress: Progress = STUB_PROGRESS, start: bool = __debug__
) -> Generator[PROFILER_TYPE, None, None]:
    """Returns a profiler and optionally starts it."""
    pr: PROFILER_TYPE = profile.Profile()

    if PYTHON_PROFILER:  # pragma: no cover
        calibration_task = progress.add_task("Calibrating...", total=5)
        for _ in progress.track(range(5), 5, task_id=calibration_task):
            pr.calibrate(10000)  # type: ignore  # cProfile doesn't have calibrate
        progress.remove_task(calibration_task)

    if start:
        # In production, we may not want to start the profiler to avoid the overhead
        pr.enable()

    yield pr

    if start:
        pr.disable()


__all__ = ("PROFILER_TYPE", "prepare_profiler")
