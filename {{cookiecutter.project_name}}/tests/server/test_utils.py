import asyncio
import copy
import os
from typing import Optional
from typing import cast
from unittest.mock import MagicMock

import pytest
import uvicorn
from fastapi import FastAPI
from fastapi import Request

from {{cookiecutter.package_name}}.server.fastapi import app
from {{cookiecutter.package_name}}.server.utils.config import ENVIRON_PREFIX
from {{cookiecutter.package_name}}.server.utils.config import build_postgres_uri
from {{cookiecutter.package_name}}.server.utils.config import build_rabbitmq_uri
from {{cookiecutter.package_name}}.server.utils.config import get_environment_override
from {{cookiecutter.package_name}}.server.utils.config import validate_bind_port
from {{cookiecutter.package_name}}.server.utils.database import create_async_sqlalchemy_engine
from {{cookiecutter.package_name}}.server.utils.fastapi import get_app_of_object
from {{cookiecutter.package_name}}.server.utils.fastapi import get_fastapi_uvicorn_config
from {{cookiecutter.package_name}}.server.utils.fastapi import mutate_fastapi_app
from {{cookiecutter.package_name}}.server.utils.prometheus import create_prometheus_app
from {{cookiecutter.package_name}}.server.utils.uvicorn import get_uvicorn_kwargs
from {{cookiecutter.package_name}}.server.utils.uvicorn import uvicorn_serve


class TestUvicornUtils:
    def test_get_uvicorn_kwargs(self) -> None:
        kwargs = get_uvicorn_kwargs()
        assert "host" in kwargs
        # Rest of the kwargs are not critical


class TestPrometheus:
    def test_prometheus(self) -> None:
        fastapi_copy = copy.copy(app)
        prometheus_app = create_prometheus_app(
            fastapi_app=fastapi_copy, prometheus_server_host="localhost", prometheus_server_port=8080
        )
        assert isinstance(prometheus_app, uvicorn.Config)


class TestFastAPIUtils:
    def test_app_shortcut_with_app(self) -> None:
        assert get_app_of_object(app) is app

    def test_app_shortcut_with_request(self) -> None:
        mock_request = Request(scope={"type": "http", "app": app})
        assert get_app_of_object(mock_request) is app

    def test_get_fastapi_uvicorn_config(self) -> None:
        fastapi_copy = copy.copy(app)
        uvicorn_config = get_fastapi_uvicorn_config(app=fastapi_copy, port=8080, host="localhost")
        assert isinstance(uvicorn_config, uvicorn.Config)

    def test_mutate_fastapi_app(self) -> None:
        fastapi_copy = copy.copy(app)
        mock_asyncsessionmaker = MagicMock()
        mock_rabbitmq_conn = MagicMock()
        mock_redis = MagicMock()
        mutate_fastapi_app(
            app=fastapi_copy,
            sqlm_session_factory=mock_asyncsessionmaker,
            rabbitmq_conn=mock_rabbitmq_conn,
            prometheus_uri="http://localhost:8080",
            redis=mock_redis,
        )
        assert fastapi_copy.state.sqlm is mock_asyncsessionmaker
        assert fastapi_copy.state.rmq is mock_rabbitmq_conn
        assert fastapi_copy.state.prom == "http://localhost:8080"
        assert fastapi_copy.state.redis is mock_redis


class TestConfigUtils:
    @pytest.mark.parametrize(
        "port,expected",
        [
            (8080, True),
            (65535, True),
            (0, False),
            (-1, False),
            (65536, False),
        ],
    )
    def test_ports(self, port: int, expected: bool) -> None:
        try:
            assert validate_bind_port(port) == expected
        except (ValueError, PermissionError):
            assert not expected

    def test_environment_override(self) -> None:
        # first mock the environment variable
        os.environ[f"{ENVIRON_PREFIX}TEST"] = "test"
        # then test the function
        assert get_environment_override("TEST", str, "test2") == "test"
        # then test the default
        assert get_environment_override("TEST2", str, "test2") == "test2"

        # test int
        os.environ[f"{ENVIRON_PREFIX}TEST_INT"] = "1"
        assert get_environment_override("TEST_INT", int, 2) == 1
        # test float
        os.environ[f"{ENVIRON_PREFIX}TEST_FLOAT"] = "1.0"
        assert get_environment_override("TEST_FLOAT", float, 2.0) == 1.0
        # test bool
        os.environ[f"{ENVIRON_PREFIX}TEST_BOOL"] = "true"
        assert get_environment_override("TEST_BOOL", bool, False) is True

        # test invalid type
        with pytest.raises(TypeError):
            get_environment_override("TEST", list, [])

        # test optional
        assert get_environment_override("TEST3", Optional[str], None) is None
        assert get_environment_override("TEST3", Optional[str], "test") == "test"
        with pytest.raises(ValueError):
            get_environment_override("TEST3", str, None)

    def test_build_postgres_uri(self) -> None:
        uri = build_postgres_uri()

    def test_build_rabbitmq_uri(self) -> None:
        uri = build_rabbitmq_uri()
