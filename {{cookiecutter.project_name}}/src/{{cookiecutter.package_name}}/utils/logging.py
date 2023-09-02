"""FastAPI utilities for Fastapipostgres - Fastapipostgres.

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
import logging

import typer
from dislog import DiscordWebhookHandler
from rich.logging import RichHandler


logger = logging.getLogger(__name__)


def get_log_level() -> int:  # pragma: no cover
    """Returns the log level for the local logger."""
    return logging.getLogger().getEffectiveLevel()


def get_safe_log_level() -> int:  # pragma: no cover
    """Returns the log level for the remote logger."""
    return max(get_log_level(), logging.INFO)


def get_library_log_level() -> int:  # pragma: no cover
    """Returns the log level for dependencies."""
    return get_log_level() + 10


def silence_library_loggers() -> None:
    """Silences loggers of dependencies to keep the log focused on the app being run."""
    dependency_loggers: set[logging.Logger] = {
        logging.getLogger("sqlalchemy"),
        logging.getLogger("discord"),
        logging.getLogger("aiohttp"),
    }
    for dependency_logger in dependency_loggers:
        dependency_logger.setLevel(get_library_log_level())
        for handler in dependency_logger.handlers:
            dependency_logger.removeHandler(handler)


def configure_rich_logger(desired_log_level: str | int) -> RichHandler:
    """Configures the local rich logger and configures backend logging."""
    log_level_int: int
    if isinstance(desired_log_level, str):
        level_name_map = logging.getLevelNamesMapping()
        if desired_log_level not in level_name_map:  # pragma: no cover
            raise typer.BadParameter(f"Invalid log level {desired_log_level!r}.")
        log_level_int = level_name_map[desired_log_level]
    elif isinstance(desired_log_level, int):
        log_level_int = desired_log_level
    else:  # pragma: no cover
        raise ValueError(f"Invalid log level {desired_log_level!r}.")
    local_logger = RichHandler(level=log_level_int)
    logging.basicConfig(level=log_level_int, handlers=[local_logger])
    silence_library_loggers()
    return local_logger


async def add_remote_logger(discord_webhook_url: str) -> DiscordWebhookHandler:
    """Configures a DisLog remote logger."""
    loop = asyncio.get_running_loop()

    # Set up logging

    # Remote logger setup needs to be done in an async context
    # It needs to setup async timers w/ asyncio
    # This code has been time-tested in other production apps and does not need to be tested in this project
    remote_logger = DiscordWebhookHandler(discord_webhook_url, level=get_safe_log_level(), event_loop=loop)

    logging.Logger.root.addHandler(remote_logger)

    logger.info("Remote logger configured.")

    return remote_logger


__all__ = (
    "get_log_level",
    "get_safe_log_level",
    "get_library_log_level",
    "silence_library_loggers",
    "add_remote_logger",
    "configure_rich_logger",
)
