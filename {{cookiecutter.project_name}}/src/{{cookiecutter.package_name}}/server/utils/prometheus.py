"""Prometheus tooling & instrumentation for {{ cookiecutter.friendly_name }} - {{ cookiecutter.description }}.

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

import prometheus_client
import uvicorn
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from uvicorn import Config

from .config import validate_bind_port
from .uvicorn import get_uvicorn_kwargs


def create_prometheus_app(fastapi_app: FastAPI, prometheus_server_host: str, prometheus_server_port: int) -> Config:
    """Creates the Prometheus app and returns a Uvicorn config for it."""
    validate_bind_port(port=prometheus_server_port)
    prometheus_registry = prometheus_client.CollectorRegistry()
    prometheus_fastapi_instrumentator = Instrumentator(registry=prometheus_registry)
    prometheus_fastapi_instrumentator.instrument(fastapi_app)
    prometheus_app = prometheus_client.make_asgi_app(registry=prometheus_registry)
    prometheus_uvicorn_kwargs = get_uvicorn_kwargs(host=prometheus_server_host)
    prometheus_uvicorn_config = uvicorn.Config(
        app=prometheus_app,
        port=prometheus_server_port,
        workers=1,
        **prometheus_uvicorn_kwargs,
    )
    return prometheus_uvicorn_config


__all__ = ("create_prometheus_app",)
