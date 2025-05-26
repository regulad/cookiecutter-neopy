"""{{ cookiecutter.friendly_name }}

Copyright (C) {{ cookiecutter.copyright_year }}  {{ cookiecutter.author }}

SPDX-License-Identifier: {% if cookiecutter.license == 'AGPL-3.0-or-later' -%}AGPL-3.0-or-later{%- endif %}{% if cookiecutter.license == 'Apache-2.0' -%}Apache-2.0{%- endif %}{% if cookiecutter.license == 'GPL-3.0-or-later' -%}GPL-3.0-or-later{%- endif %}{% if cookiecutter.license == 'MIT' -%}MIT{%- endif %}
"""  # noqa: E501, B950, D415

from __future__ import annotations

import logging


try:
    from importlib.metadata import PackageMetadata
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import metadata as __load
except ImportError:  # pragma: no cover
    from importlib_metadata import PackageMetadata  # type: ignore
    from importlib_metadata import PackageNotFoundError  # type: ignore
    from importlib_metadata import metadata as __load  # type: ignore


logger = logging.getLogger(__package__)
try:
    metadata: PackageMetadata = __load(__package__)
    __uri__ = metadata["home-page"]
    __title__ = metadata["name"]
    __summary__ = metadata["summary"]
    __license__ = metadata["license"]
    __version__ = metadata["version"]
    __author__ = metadata["author"]
    __maintainer__ = metadata["maintainer"]
    __contact__ = metadata["maintainer"]
except PackageNotFoundError:  # pragma: no cover
    # fmt: off
    logger.error(f"Could not load package metadata for {__package__}. Is it installed?")
    logger.debug("Falling back to static metadata.")
    __uri__ = ""
    __title__ = "{{ cookiecutter.friendly_name }}"
    __summary__ = "{{ cookiecutter.description }}"
    __license__ = "{{ cookiecutter.license }}"
    __version__ = "0.0.0"
    __author__ = "{{ cookiecutter.author }}"
    __maintainer__ = "{{ cookiecutter.author }}"
    __contact__ = "{{ cookiecutter.author }}"
    # fmt: on
__copyright__ = "Copyright {{ cookiecutter.copyright_year }}"


__all__ = (
    "__copyright__",
    "__uri__",
    "__title__",
    "__summary__",
    "__license__",
    "__version__",
    "__author__",
    "__maintainer__",
    "__contact__",
)
