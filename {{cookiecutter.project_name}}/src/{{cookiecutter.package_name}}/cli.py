"""CLI for {{ cookiecutter.friendly_name }} - {{ cookiecutter.description }}.

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

import asyncio
import copy
import json
import logging
import pstats
from os import environ
from typing import Optional

import aio_pika
import redis.asyncio as redis
import typer
from anyio import Event
from anyio import create_task_group
from rich.progress import Progress
from sqlalchemy.ext.asyncio import AsyncEngine  # noqa: F401  # ignores type string
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: F401  # ignores type string

from ._assets import RESOURCES
from ._metadata import __title__
from .server.fastapi import app as static_app
from .server.utils.config import ENVIRON_PREFIX
from .server.utils.config import build_postgres_uri
from .server.utils.config import build_rabbitmq_uri
from .server.utils.config import get_environment_override
from .server.utils.database import create_async_sqlalchemy_engine
from .server.utils.database import make_session_factory
from .server.utils.database import run_migrations
from .server.utils.fastapi import get_fastapi_uvicorn_config
from .server.utils.fastapi import mutate_fastapi_app
from .server.utils.prometheus import create_prometheus_app
from .server.utils.uvicorn import uvicorn_serve
from .utils.asyncio import make_async
from .utils.asyncio import make_sync
from .utils.asyncio import signal_handler
from .utils.logging import add_remote_logger
from .utils.logging import configure_rich_logger
from .utils.profiling import PROFILER_TYPE  # noqa: F401
from .utils.profiling import prepare_profiler


cli = typer.Typer()
logger = logging.getLogger(__name__)


@cli.command()
def main() -> None:
    data = RESOURCES / "data.json"
    with data.open() as json_fp:
        parsed = json.load(json_fp)
    status = parsed["status"]
    print(typer.style(status, fg=typer.colors.GREEN, bold=True))


@cli.command()
@make_sync
async def serve(
    log_level: str = "INFO",
    dislog: Optional[str] = None,
    host: str = "0.0.0.0",  # nosec # B104:hardcoded_bind_all_interfaces
    port: int = 8080,
    *,
    # Postgres
    postgres_host: str = "localhost",
    postgres_port: int = 5432,
    postgres_user: str = __title__,
    postgres_password: str = __title__,
    postgres_db: str = __title__,
    # RabbitMQ
    rabbitmq_host: str = "localhost",
    rabbitmq_port: int = 5672,
    rabbitmq_user: str = __title__,
    rabbitmq_password: str = __title__,
    rabbitmq_vhost: str = __title__,
    # Redis
    redis_host: str = "localhost",
    redis_port: int = 6379,
    redis_user: Optional[str] = None,  # __title__
    redis_password: Optional[str] = None,  # __title__
    redis_db: int = 0,
    # Prometheus client
    prometheus_host: str = "localhost",
    prometheus_port: int = 9090,
    # Prometheus server
    prometheus_server_port: int = 8000,
) -> None:  # pragma: no cover
    """Serve a webserver that allows other programs to access the features of the package."""
    # This function is not tested because it is a CLI entrypoint. It will be tested in manual integration tests.
    # Attempt to get configuration from environment variables if missing in CLI.
    log_level = get_environment_override("LOG_LEVEL", str, log_level).upper()

    host = get_environment_override("HOST", str, host)
    port = get_environment_override("PORT", int, port)

    prometheus_host = get_environment_override("PROMETHEUS_HOST", str, prometheus_host)
    prometheus_port = get_environment_override("PROMETHEUS_PORT", int, prometheus_port)

    redis_host = get_environment_override("REDIS_HOST", str, redis_host)
    redis_port = get_environment_override("REDIS_PORT", int, redis_port)
    redis_user = get_environment_override("REDIS_USER", Optional[str], redis_user)
    redis_password = get_environment_override("REDIS_PASSWORD", Optional[str], redis_password)
    redis_db = get_environment_override("REDIS_DB", int, redis_db)

    # Start doing work here now that we have the configuration
    loop = asyncio.get_event_loop()
    app = copy.copy(static_app)

    # Logging
    configure_rich_logger(log_level)
    logger.info("Local logger configured.")
    logger.info(f"Starting {__title__}...")

    # Configure the server
    uvicorn_config = get_fastapi_uvicorn_config(app, port, host)

    # determine if a Discord remote logger has been configured, and if it has, use it
    dislog_env = environ.get(f"{ENVIRON_PREFIX}DISLOG")
    if dislog_env is not None and dislog is None:  # pragma: no cover
        dislog = dislog_env
    if dislog is not None:  # pragma: no cover
        await add_remote_logger(dislog)

    # RabbitMQ configuration
    logger.info("Connecting to RabbitMQ...")
    rabbitmq_uri = build_rabbitmq_uri(
        rabbitmq_host=rabbitmq_host,
        rabbitmq_password=rabbitmq_password,
        rabbitmq_port=rabbitmq_port,
        rabbitmq_user=rabbitmq_user,
        rabbitmq_vhost=rabbitmq_vhost,
    )
    rabbitmq_conn = await aio_pika.connect_robust(rabbitmq_uri, loop=loop)
    logger.info("RabbitMQ connection successful.")

    # Redis configuration
    logger.info("Connecting to Redis...")
    redis_conn = redis.Redis(
        host=redis_host,
        port=redis_port,
        username=redis_user,
        password=redis_password,
        db=redis_db,
        protocol=3,
    )
    await redis_conn.ping()
    logger.info("Redis connection successful.")

    # Postgres/SQLAlchemy setup
    logger.info("Connecting to Postgres...")
    postgres_uri = build_postgres_uri(
        postgres_db=postgres_db,
        postgres_host=postgres_host,
        postgres_password=postgres_password,
        postgres_port=postgres_port,
        postgres_user=postgres_user,
    )
    pg_engine = await create_async_sqlalchemy_engine(postgres_uri)
    logger.info("Postgres connection successful.")
    # Run migrations
    logger.info("Running migrations...")
    await make_async(run_migrations)(postgres_uri)  # type: ignore
    logger.info("Migrations complete.")

    # Prometheus client configuration
    prometheus_uri = f"http://{prometheus_host}:{prometheus_port}"
    # Prometheus server configuration
    prometheus_server_port = get_environment_override("PROMETHEUS_SERVER_PORT", int, prometheus_server_port)
    prometheus_uvicorn_config = create_prometheus_app(app, host, prometheus_server_port)

    # Attach the databases to the app
    # You can attach sister services here as well like a Discord bot
    # Make sure to also add these to .fastapi_utils
    sqlm_session_factory = await make_session_factory(pg_engine)
    mutate_fastapi_app(
        app,
        sqlm_session_factory=sqlm_session_factory,
        rabbitmq_conn=rabbitmq_conn,
        prometheus_uri=prometheus_uri,
        redis=redis_conn,
    )

    # Advice on handling profiling in asyncio code: https://www.roguelynn.com/words/asyncio-profiling/
    with Progress() as progress, prepare_profiler(progress) as pr:
        # Start the server and any sister services
        # Because this template focuses on sister services and interaction,
        # we are not using a process manager like Gunicorn.
        # Instead, our code is optimized to work in a single process that is replicated
        # using a process manager like systemd, Docker Compose, or Kubernetes.
        shutdown_event = Event()
        logger.info("Starting server...")
        async with create_task_group() as tg:
            # Schedule any sister services here to have them run concurrently with the server
            # =============================
            # When more than one task is loaded in a task group, for some reason only the most recently created task
            # is capable of receiving signals, and other tasks will not receive them.
            # I'm not sure why, and I could only find this on macOS.
            await tg.start(uvicorn_serve, uvicorn_config, shutdown_event, name="api")
            await tg.start(uvicorn_serve, prometheus_uvicorn_config, shutdown_event, name="prometheus")
            await tg.start(signal_handler, tg.cancel_scope, shutdown_event, name="signal_handler")

            # Log the startup and wait for the services to finish
            logger.info("Server started.")
            await shutdown_event.wait()

    # Cleanup & shutdown
    await rabbitmq_conn.close()
    await pg_engine.dispose()

    if __debug__:
        logger.info("Profiling results:")
        pr.create_stats()
        stats = pstats.Stats(pr)
        stats.sort_stats(pstats.SortKey.CUMULATIVE)
        stats.print_stats(0.05)


if __name__ == "__main__":  # pragma: no cover
    cli()

__all__ = ("cli",)
