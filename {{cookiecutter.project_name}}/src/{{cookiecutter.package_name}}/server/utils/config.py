"""Configuration utilities for {{ cookiecutter.friendly_name }} - {{ cookiecutter.description }}.

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

import os
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import _UnionGenericAlias as OptionalType  # type: ignore
from urllib.parse import quote

from ..._metadata import __title__


ENVIRON_PREFIX = "{{cookiecutter.environ_prefix}}"


def validate_bind_port(port: int) -> bool:
    """Validates a port number, making sure it is valid and that we can bind to it."""
    if port < 1 or port > 65535:  # pragma: no cover
        raise ValueError(f"Port {port} is not in the range 1-65535.")
    elif port < 1024 and os.name != "nt":  # pragma: no cover
        # Check to see if we are root and can bind to a privileged port.
        try:
            if os.getuid() != 0:
                raise PermissionError(f"You must be root to bind to privileged port {port}.")
        except AttributeError:
            # Weird OS implementation?
            pass
    return True


VARIABLE_TYPE = TypeVar("VARIABLE_TYPE")


def get_environment_override(
    variable_name: str, variable_type: Type[VARIABLE_TYPE] | OptionalType, default: VARIABLE_TYPE
) -> VARIABLE_TYPE:
    """Check an environment variable for an overridden CLI flag."""
    is_optional: bool = variable_type.__module__ == "typing" and variable_type.__name__ == "Optional"
    if is_optional:
        variable_type = variable_type.__args__[0]  # type: ignore
    variable_fully_qualified_name = f"{ENVIRON_PREFIX}{variable_name.upper()}"
    default_string: Optional[str] = str(default) if variable_type is not str and default is not None else default  # type: ignore
    variable_value: Optional[str] = os.environ.get(variable_fully_qualified_name, default_string)
    if is_optional and variable_value is None:
        return None  # type: ignore
    elif not is_optional and variable_value is None:
        raise ValueError(f"Environment variable {variable_fully_qualified_name} is not set and has no default.")
    elif variable_type is bool:
        return variable_value.lower() in ("true", "1", "yes")  # type: ignore
    elif variable_type is int:
        return int(variable_value)  # type: ignore
    elif variable_type is float:
        return float(variable_value)  # type: ignore
    elif variable_type is str:
        return variable_value  # type: ignore
    else:
        raise TypeError(f"Variable type {variable_type} is not supported.")


def build_postgres_uri(
    *,
    postgres_host: str = "localhost",
    postgres_port: int = 5432,
    postgres_user: str = __title__,
    postgres_password: str = __title__,
    postgres_db: str = __title__,
) -> str:
    """Builds a Postgres URI from the given parameters. Respects environment variables."""
    postgres_host = get_environment_override("POSTGRES_HOST", str, postgres_host)
    postgres_port = get_environment_override("POSTGRES_PORT", int, postgres_port)
    postgres_user = get_environment_override("POSTGRES_USER", str, postgres_user)
    postgres_password = get_environment_override("POSTGRES_PASSWORD", str, postgres_password)
    postgres_db = get_environment_override("POSTGRES_DB", str, postgres_db)
    # Username and password may contain special characters that need to be escaped
    postgres_user_escaped = quote(postgres_user)
    postgres_password_escaped = quote(postgres_password)
    # Build the Postgres URI
    postgres_uri = (
        f"postgresql+asyncpg://"
        f"{postgres_user_escaped}:{postgres_password_escaped}"
        f"@{postgres_host}:{postgres_port}"
        f"/{postgres_db}"
    )
    return postgres_uri


def build_rabbitmq_uri(
    *,
    rabbitmq_host: str = "localhost",
    rabbitmq_port: int = 5672,
    rabbitmq_user: str = __title__,
    rabbitmq_password: str = __title__,
    rabbitmq_vhost: str = __title__,
) -> str:
    """Builds a RabbitMQ URI from the given parameters. Respects environment variables."""
    rabbitmq_host = get_environment_override("RABBITMQ_HOST", str, rabbitmq_host)
    rabbitmq_port = get_environment_override("RABBITMQ_PORT", int, rabbitmq_port)
    rabbitmq_user = get_environment_override("RABBITMQ_USER", str, rabbitmq_user)
    rabbitmq_password = get_environment_override("RABBITMQ_PASSWORD", str, rabbitmq_password)
    rabbitmq_vhost = get_environment_override("RABBITMQ_VHOST", str, rabbitmq_vhost)
    rabbitmq_user_escaped = quote(rabbitmq_user)
    rabbitmq_password_escaped = quote(rabbitmq_password)
    rabbitmq_uri = (
        f"amqp://{rabbitmq_user_escaped}:{rabbitmq_password_escaped}"
        f"@{rabbitmq_host}:{rabbitmq_port}"
        f"/{rabbitmq_vhost}"
    )
    return rabbitmq_uri


__all__ = (
    "validate_bind_port",
    "get_environment_override",
    "ENVIRON_PREFIX",
    "build_postgres_uri",
    "build_rabbitmq_uri",
)
