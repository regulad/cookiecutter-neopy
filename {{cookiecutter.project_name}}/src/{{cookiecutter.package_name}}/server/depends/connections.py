"""Database connection code for {{ cookiecutter.friendly_name }} - {{ cookiecutter.description }}.

{% if cookiecutter.license == 'Apache-2.0' -%}Copyright {{ cookiecutter.copyright_year }} {{ cookiecutter.author }}

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.{%- endif %}{% if cookiecutter.license == 'GPL-3.0' -%}Copyright (C) {{ cookiecutter.copyright_year }}  {{ cookiecutter.author }}

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.{%- endif %}{% if cookiecutter.license == 'MIT' -%}MIT License

Copyright © {{ cookiecutter.copyright_year }} {{ cookiecutter.author }}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.{%- endif %}
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
