"""External connections & database dependencies for Fastapipostgres - Fastapipostgres.

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

from typing import AsyncGenerator

from aio_pika.abc import AbstractRobustConnection
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette.requests import Request

from ..utils.fastapi import get_app_of_object


async def get_sqlmodel_session(request: Request) -> AsyncGenerator[AsyncSession, None]:  # pragma: no cover
    """Get a SQLModel session."""
    factory: sessionmaker = get_app_of_object(request).state.sqlm  # type: ignore
    async with factory() as session:  # type: AsyncSession
        # All initiation/destruction of the session is handled by the factory
        yield session


def get_rabbitmq_conn(request: Request) -> AbstractRobustConnection:  # pragma: no cover
    """Get a RabbitMQ connection."""
    return get_app_of_object(request).state.rmq  # type: ignore


def get_prometheus_uri(request: Request) -> str:  # pragma: no cover
    """Get a Prometheus URI."""
    return get_app_of_object(request).state.prom  # type: ignore


def get_redis_connection(request: Request) -> Redis:  # pragma: no cover
    """Get a Redis connection."""
    return get_app_of_object(request).state.redis  # type: ignore


__all__ = (
    "get_sqlmodel_session",
    "get_rabbitmq_conn",
    "get_prometheus_uri",
    "get_redis_connection",
)
