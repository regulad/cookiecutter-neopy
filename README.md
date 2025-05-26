# cookiecutter-neopy

Hi there!
I'm an amateur Python developer, and I love [`tyrannosaurus`](https://github.com/dmyersturnbull/tyrannosaurus), 
and equally love [`cookiecutter-hypermodern-python`](https://cookiecutter-hypermodern-python.readthedocs.io/en/2022.6.3.post1/).
However, in my extended use of both, I noticed some shortcomings that I wanted to address.

1. `tyrannosaurus` uses its own templating engine, but it unfortunately is very buggy and most of its exclusive features (like sync) are poorly implemented. I wanted to use `cookiecutter`'s templating engine, which is much more robust and well-maintained.
2. `tyrannosaurus` tries too hard to make testing into a monolith, which yields unintelligible test results. Even though I prefer tox over nox, I still chose to take `cookiecutter-hypermodern-python`'s approach of using nox, because it's much more flexible and easier to use.
3. `tyrannosaurus` never seems to update its dependencies, and it's stuck on Python 3.8. I wanted to use Python 3.11 **exclusively** to make use of the increased performance and syntax features, and I wanted to use the latest versions of all the dependencies.
4. `tyrannosaurus` has a lot of boilerplate code pre-included, mainly for capturing test data and retrieving assets. While this is a good idea. It doesn't help that half of it is wrong and fails its own type checks. 🙃 The boilerplate I chose to implement in my template is a lot lighter and only supplies things that EVERY project uses.
5. `cookiecutter-hypermodern-python` is a great template, but it lacks the tooling for containerization and deployment with Docker like `tyrannosaurus` has. I wanted to add that to this template.
6. `cookiecutter-hypermodern-python` also favors lower-level libraries like click over higher-level libraries like typer. I wanted to use typer, because it's a great library that makes it easy to build CLI applications.

For all of these reasons, I decided to fork `cookiecutter-hypermodern-python` and make my own template, `cookiecutter-neopy`. I hope you enjoy it!

## TODO

- [x] Convert to Python 3.11
- [x] Update dependencies
- [x] Add settings.yml for GitHub Probot
- [x] Add `typer`
- [x] Add Dockerfile
- [x] Add docker-compose.yml
- [x] Add GitHub Actions for publishing Docker image
- [x] Write typer boilerplate & tests
- [x] Write asset & metadata boilerplate & tests

## Usage

```console
# install pip & pipx through your distribution's package manager
pipx install poetry
pipx inject poetry poetry-plugin-export

pipx install nox
pipx inject nox nox-poetry

pipx install cookiecutter

# confirm poetry can find both Python~3.11 and Python~3.12
pipx python list

cookiecutter gh:regulad/cookiecutter-neopy
```

Please note, you must have the following installed and on `PATH`: `nox`, `Python 3.11/3.12`, `poetry` & `git`

The following segment of the README is the original README from `cookiecutter-hypermodern-python`.

<hr/>

# cookiecutter-hypermodern-python

<!-- badges-begin -->

[![Status][status badge]][status badge]
[![Python Version][python version badge]][github page]
[![CalVer][calver badge]][calver]
[![License][license badge]][license]<br>
[![Read the documentation][readthedocs badge]][readthedocs page]
[![Tests][github actions badge]][github actions page]
[![Codecov][codecov badge]][codecov page]<br>
[![pre-commit enabled][pre-commit badge]][pre-commit project]
[![Black codestyle][black badge]][black project]
[![Contributor Covenant][contributor covenant badge]][code of conduct]

[black badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[black project]: https://github.com/psf/black
[calver badge]: https://img.shields.io/badge/calver-YYYY.MM.DD-22bfda.svg
[calver]: http://calver.org/
[code of conduct]: https://github.com/cjolowicz/cookiecutter-hypermodern-python/blob/main/CODE_OF_CONDUCT.md
[codecov badge]: https://codecov.io/gh/cjolowicz/cookiecutter-hypermodern-python-instance/branch/main/graph/badge.svg
[codecov page]: https://codecov.io/gh/cjolowicz/cookiecutter-hypermodern-python-instance
[contributor covenant badge]: https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg
[github actions badge]: https://github.com/cjolowicz/cookiecutter-hypermodern-python/workflows/Tests/badge.svg
[github actions page]: https://github.com/cjolowicz/cookiecutter-hypermodern-python/actions?workflow=Tests
[github page]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[license badge]: https://img.shields.io/github/license/cjolowicz/cookiecutter-hypermodern-python
[license]: https://opensource.org/licenses/MIT
[pre-commit badge]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
[pre-commit project]: https://pre-commit.com/
[python version badge]: https://img.shields.io/pypi/pyversions/cookiecutter-hypermodern-python-instance
[readthedocs badge]: https://img.shields.io/readthedocs/cookiecutter-hypermodern-python/latest.svg?label=Read%20the%20Docs
[readthedocs page]: https://cookiecutter-hypermodern-python.readthedocs.io/
[status badge]: https://badgen.net/badge/status/alpha/d8624d

<!-- badges-end -->

<p align="center"><img alt="logo" src="docs/_static/logo.png" width="50%" /></p>

[Cookiecutter] template for a Python package based on the
[Hypermodern Python] article series.

✨📚✨ [Read the full documentation][readthedocs page]

[cookiecutter]: https://github.com/audreyr/cookiecutter
[hypermodern python]: https://medium.com/@cjolowicz/hypermodern-python-d44485d9d769

## Usage

```console
cookiecutter gh:cjolowicz/cookiecutter-hypermodern-python --checkout=2022.8.23
```

Special branches in the `frameworks` folder are available for some Python frameworks like FastAPI, Discord.py, and more. Check GitHub to see if there's a branch for your framework of choice.

These special templates also carry the opinionated nature of the base template, so you can expect the same quality of code and documentation.

```console
cookiecutter gh:cjolowicz/cookiecutter-hypermodern-python --checkout=frameworks/fastapi
```

## Features

<!-- features-begin -->

- Packaging and dependency management with [Poetry]
- Test automation with [Nox]
- Linting with [pre-commit] and [Flake8]
- Continuous integration with [GitHub Actions]
- Documentation with [Sphinx], [MyST], and [Read the Docs] using the [furo] theme
- Automated uploads to [PyPI] and [TestPyPI]
- Automated release notes with [Release Drafter]
- Automated dependency updates with [Dependabot]
- Code formatting with [Black] and [Prettier]
- Import sorting with [isort]
- Testing with [pytest]
- Code coverage with [Coverage.py]
- Coverage reporting with [Codecov]
- Command-line interface with [Click]
- Static type-checking with [mypy]
- Runtime type-checking with [Typeguard]
- Automated Python syntax upgrades with [pyupgrade]
- Security audit with [Bandit] and [Safety]
- Check documentation examples with [xdoctest]
- Generate API documentation with [autodoc] and [napoleon]
- Generate command-line reference with [sphinx-click]
- Manage project labels with [GitHub Labeler]

The template supports Python 3.7, 3.8, 3.9, and 3.10.

[autodoc]: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
[bandit]: https://github.com/PyCQA/bandit
[black]: https://github.com/psf/black
[click]: https://click.palletsprojects.com/
[codecov]: https://codecov.io/
[coverage.py]: https://coverage.readthedocs.io/
[dependabot]: https://github.com/dependabot/dependabot-core
[flake8]: http://flake8.pycqa.org
[furo]: https://pradyunsg.me/furo/
[github actions]: https://github.com/features/actions
[github labeler]: https://github.com/marketplace/actions/github-labeler
[isort]: https://pycqa.github.io/isort/
[mypy]: http://mypy-lang.org/
[myst]: https://myst-parser.readthedocs.io/
[napoleon]: https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
[nox]: https://nox.thea.codes/
[poetry]: https://python-poetry.org/
[pre-commit]: https://pre-commit.com/
[prettier]: https://prettier.io/
[pypi]: https://pypi.org/
[pytest]: https://docs.pytest.org/en/latest/
[pyupgrade]: https://github.com/asottile/pyupgrade
[read the docs]: https://readthedocs.org/
[release drafter]: https://github.com/release-drafter/release-drafter
[safety]: https://github.com/pyupio/safety
[sphinx]: http://www.sphinx-doc.org/
[sphinx-click]: https://sphinx-click.readthedocs.io/
[testpypi]: https://test.pypi.org/
[typeguard]: https://github.com/agronholm/typeguard
[xdoctest]: https://github.com/Erotemic/xdoctest

<!-- features-end -->
