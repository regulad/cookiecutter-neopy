"""Test cases for the __main__ module."""

import pytest
from typer.testing import CliRunner

from {{cookiecutter.package_name}}.__main__ import cli


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


class TestCLI:
    """Test cases for the command-line interface."""

    def test_main_succeeds(self, runner: CliRunner) -> None:
        """Calls the default command and exits with a status code of zero."""
        result = runner.invoke(cli)
        assert result.exit_code == 0


__all__ = ("TestCLI",)
