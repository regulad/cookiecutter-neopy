"""Database utilities for {{ cookiecutter.friendly_name }} - {{ cookiecutter.description }}.

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

import logging
import tempfile
import typing
from importlib.resources import as_file
from pathlib import Path
from shutil import copytree
from typing import TypeAlias
from urllib import parse

from alembic import command as alembic_cmd
from alembic.config import Config as AlembicConfig
from sqlalchemy.ext.asyncio import AsyncConnection  # noqa: F401  # ignores type string
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from ..._assets import RESOURCES
from ...utils.threading import THREAD_POOL_EXECUTORS


logger = logging.getLogger(__name__)

ASYNC_SESSIONMAKER_TYPE: TypeAlias = sessionmaker[AsyncSession]  # type: ignore
ALEMBIC_POSTGRES_DRIVER = "pg8000"


# https://github.com/deshetti/sqlmodel-async-example/blob/main/main.py#L42
@typing.no_type_check
async def make_session_factory(async_engine: AsyncEngine) -> ASYNC_SESSIONMAKER_TYPE:  # pragma: no cover
    """Creates a session factory for SQLModel."""
    return sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


async def create_async_sqlalchemy_engine(dsn: str) -> AsyncEngine:  # pragma: no cover
    """Creates a SQLAlchemy engine for PostgreSQL."""
    # SQLAlchemy does not provide any mock engine for async, so we cannot test this function.
    return create_async_engine(
        dsn,
        echo=False,  # Tampers with logging configuration
        future=True,
        pool_size=THREAD_POOL_EXECUTORS,
        max_overflow=THREAD_POOL_EXECUTORS,
        pool_recycle=3600,
    )


def run_migrations(pg_url: str) -> None:  # pragma: no cover
    """Runs & generates migrations to run on the database."""
    # While this function *could* be tested, it would require a working PostgreSQL database, and there is no branching,
    # so it is not worth the effort when it can just be manually tested.
    # The main point of failure will be crappy alembic migrations,
    # which need to be manually tested anyway.
    # We need to replace asyncpg with psycopy because the Alembic template we use is sync-only for simplicity's sake.
    pg_url_parsed = parse.urlparse(pg_url)

    if not pg_url_parsed.scheme.startswith("postgresql+"):
        raise ValueError(f"Invalid PostgreSQL URL: {pg_url}")

    pg_url_parsed = pg_url_parsed._replace(scheme=f"postgresql+{ALEMBIC_POSTGRES_DRIVER}")
    good_pg_url_str = pg_url_parsed.geturl().replace("%", "%%")  # escape for the .ini file

    with as_file(RESOURCES / "alembic") as alembic_config_path, tempfile.TemporaryDirectory() as temp_dir:
        alembic_tmp_dir = Path(temp_dir) / "alembic"
        # Since we are going to be making changes to the Alembic config, we need to copy it to a temporary directory.
        copytree(alembic_config_path, alembic_tmp_dir)

        alembic_config = AlembicConfig(alembic_tmp_dir / "alembic.ini")
        alembic_config.set_main_option("sqlalchemy.url", good_pg_url_str)
        alembic_config.set_main_option("script_location", str(alembic_tmp_dir / "alembic"))
        alembic_cmd.upgrade(alembic_config, "head", tag="prod")


__all__ = ("make_session_factory", "create_async_sqlalchemy_engine", "run_migrations")
