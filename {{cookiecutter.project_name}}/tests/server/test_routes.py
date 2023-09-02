import copy
from unittest.mock import MagicMock

import pytest
from starlette.testclient import TestClient

from {{cookiecutter.package_name}}.server.fastapi import app
from {{cookiecutter.package_name}}.server.utils.fastapi import mutate_fastapi_app


@pytest.fixture
def client() -> TestClient:
    """Fixture for invoking command-line interfaces."""
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
    return TestClient(app)


class TestRoutes:
    def test_status(self, client: TestClient) -> None:
        assert True  # implement your tests here
        # https://fastapi.tiangolo.com/tutorial/testing/
