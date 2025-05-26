"""{{ cookiecutter.friendly_name }}

Copyright (C) {{ cookiecutter.copyright_year }}  {{ cookiecutter.author }}

SPDX-License-Identifier: {% if cookiecutter.license == 'AGPL-3.0-or-later' -%}AGPL-3.0-or-later{%- endif %}{% if cookiecutter.license == 'Apache-2.0' -%}Apache-2.0{%- endif %}{% if cookiecutter.license == 'GPL-3.0-or-later' -%}GPL-3.0-or-later{%- endif %}{% if cookiecutter.license == 'MIT' -%}MIT{%- endif %}
"""  # noqa: E501, B950, D415

from __future__ import annotations

from importlib.resources import files


# The root of the package. This may not be a path if the package is installed, so just access the Traversable.
PACKAGE = files(__package__)
# If you use all of your files in a folder like `assets` or `resources` (recommended), use the following line.
RESOURCES = PACKAGE / "resources"

__all__ = ("RESOURCES",)
