"""{{ cookiecutter.friendly_name }}

Copyright (C) {{ cookiecutter.copyright_year }}  {{ cookiecutter.author }}

SPDX-License-Identifier: {% if cookiecutter.license == 'AGPL-3.0-or-later' -%}AGPL-3.0-or-later{%- endif %}{% if cookiecutter.license == 'Apache-2.0' -%}Apache-2.0{%- endif %}{% if cookiecutter.license == 'GPL-3.0-or-later' -%}GPL-3.0-or-later{%- endif %}{% if cookiecutter.license == 'MIT' -%}MIT{%- endif %}
"""  # noqa: E501, B950, D415

from __future__ import annotations

import json

import typer

from ._assets import RESOURCES
from ._metadata import __version__


cli = typer.Typer()


@cli.command()
def main() -> None:
    data = RESOURCES / "data.json"
    with data.open() as json_fp:
        parsed = json.load(json_fp)
    status = parsed["status"]
    print(__version__ + " " + typer.style(status, fg=typer.colors.GREEN, bold=True))


if __name__ == "__main__":  # pragma: no cover
    cli()

__all__ = ("cli",)
