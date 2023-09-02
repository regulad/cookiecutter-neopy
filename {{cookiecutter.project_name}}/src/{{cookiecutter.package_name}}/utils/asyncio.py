"""AsyncIO utilities for Fastapipostgres - Fastapipostgres.

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

import asyncio
import functools
import logging
import platform
import signal
import sys
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from typing import Callable
from typing import Coroutine
from typing import ParamSpec
from typing import TypeVar

import anyio
from anyio import TASK_STATUS_IGNORED
from anyio import CancelScope
from anyio import Event
from anyio import open_signal_receiver
from anyio.abc import TaskStatus

from .threading import THREAD_POOL_EXECUTORS


try:
    import uvloop  # noqa: F401
except ImportError:  # pragma: no cover
    pass

UVLOOP_INSTALLED = "uvloop" in sys.modules

logger = logging.getLogger(__name__)


def _can_use_uvloop() -> bool:
    """Check to see if uvloop can be used."""
    use_uvloop: bool = False
    if (
        sys.version_info < (3, 12)
        and not sys.platform.lower().startswith("win")
        and platform.python_implementation() == "CPython"
        and UVLOOP_INSTALLED
    ):  # pragma: no cover
        # all of these are required for uvloop to work
        use_uvloop = True
    return use_uvloop


CAN_USE_UVLOOP = _can_use_uvloop()

A_RETVAL = TypeVar("A_RETVAL")


@asynccontextmanager
async def _async_lifespan_manager() -> AsyncGenerator[None, None]:
    """Async context manager for the lifespan of the application."""
    loop = asyncio.get_running_loop()

    # Setup a more managed ThreadPoolExecutor
    # asyncio actually manages the lifespan of the default executor, but it's not very good at it.
    with ThreadPoolExecutor(max_workers=THREAD_POOL_EXECUTORS, thread_name_prefix="asyncio_thread") as executor:
        loop.set_default_executor(executor)
        yield


def run_coroutine_managed(coro: Callable[[], Coroutine[None, None, A_RETVAL]]) -> A_RETVAL:
    """Manages running a coroutine with an async context manager making starting it from sync contexts easy as pie!"""
    # https://github.com/aio-libs/aiopg/issues/678
    if sys.version_info >= (3, 8) and sys.platform.lower().startswith("win"):  # pragma: no cover
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # type: ignore

    async def _async_bootstrap() -> A_RETVAL:
        async with _async_lifespan_manager():
            return await coro()

    return anyio.run(
        _async_bootstrap,
        backend="asyncio",
        backend_options={
            "debug": __debug__,
            "use_uvloop": CAN_USE_UVLOOP,
        },
    )


async def signal_handler(
    cancel_scope: CancelScope,
    event: Event,
    *,
    task_status: TaskStatus[None] = TASK_STATUS_IGNORED,
) -> None:  # pragma: no cover
    """Handles KeyboardInterrupts by cancelling the cancel scope and setting the event.

    Args:
        cancel_scope (CancelScope): The cancel scope to cancel.
        event (Event): The event to set.
        task_status (TaskStatus[None], optional): The task status to set. Defaults to TASK_STATUS_IGNORED.
    """
    # Not sure how I would test this, so I'm just going to ignore it and hope it works
    async with open_signal_receiver(signal.SIGINT, signal.SIGTERM) as signals:
        task_status.started()
        async for signum in signals:
            # We have recieved a shutdown signal, so we need to cancel the cancel scope
            if signum == signal.SIGINT:
                logger.info("Received SIGINT, shutting down...")
            elif signum == signal.SIGTERM:
                logger.info("Received SIGTERM, shutting down...")
            await event.set()
            # await cancel_scope.cancel()
            return


P = ParamSpec("P")
R = TypeVar("R")


@functools.lru_cache(maxsize=None)  # type: ignore
def make_sync(coro: Callable[P, Coroutine[None, None, R]]) -> Callable[P, R]:
    """A decorator that wraps an async function and abstracts away event loop & cancel scope creation."""

    @functools.wraps(coro)
    def sync_function(*args: P.args, **kwargs: P.kwargs) -> R:
        return run_coroutine_managed(functools.partial(coro, *args, **kwargs))

    # Special marker values to make testing easier
    sync_function.__is_wrapped__ = True  # type: ignore
    sync_function.__async_function__ = coro  # type: ignore

    return sync_function


@functools.lru_cache(maxsize=None)  # type: ignore
def make_async(func: Callable[P, R]) -> Callable[P, Coroutine[None, None, R]]:
    """A decorator that wraps a sync function and abstracts away calling it in an executor."""
    return functools.wraps(func)(functools.partial(asyncio.to_thread, func))


__all__ = ("run_coroutine_managed", "signal_handler", "make_sync", "make_async")
