#!/usr/bin/env python
import json
import subprocess
from pathlib import Path


def reindent_cookiecutter_json():
    """Indent .cookiecutter.json using two spaces.

    The jsonify extension distributed with Cookiecutter uses an indentation
    width of four spaces. This conflicts with the default indentation width of
    Prettier for JSON files. Prettier is run as a pre-commit hook in CI.
    """
    path = Path(".cookiecutter.json")

    with path.open() as io:
        data = json.load(io)

    with path.open(mode="w") as io:
        json.dump(data, io, sort_keys=True, indent=2)
        io.write("\n")


def git_init():
    """
    Initializes the repository with git.
    """
    subprocess.run(["git", "init"], check=True, capture_output=True, stdin=subprocess.DEVNULL)
    subprocess.run(["git", "add", "."], check=True, capture_output=True, stdin=subprocess.DEVNULL)
    subprocess.run(["git", "commit", "-m", "initial commit"], check=True, capture_output=True, stdin=subprocess.DEVNULL)


def poetry_install():
    """
    Installs the project with Poetry.
    """
    subprocess.run(["poetry", "install"], check=True, capture_output=True, stdin=subprocess.DEVNULL)


def pre_commit_install():
    """
    Installs pre-commit into the repository.
    """
    subprocess.run(["poetry", "run", "pre-commit", "install"], check=True, capture_output=True,
                   stdin=subprocess.DEVNULL)


def confirm_nox_install():
    """
    Confirms that nox is installed and operating correctly.
    """
    try:
        subprocess.run(
            [
                "poetry",
                "run",
                "nox",
                "-x",
                "--error-on-missing-interpreters",
                "--error-on-external-run",
                "--non-interactive",
            ],
            check=True,
            # capture_output=True,
            stdin=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        print("Nox is not installed or is not operating correctly. "
              "Please follow cookiecutter-hypermodern-python's instructions to install it.")
        raise


def print_notices():
    """
    Prints some special notices for the user.
    """
    print()
    print("Thank you for choosing cookiecutter-neopy! Please note the following:")
    print("\t1. A GitHub repository has not been automatically created for you.")
    print("\t   You can create one manually or use the gh CLI (far faster than the website) to create one for you.")
    print("\t   https://cli.github.com/")
    print("\t2. Install probot settings into your GitHub account to enable settings.yml.")
    print("\t   https://probot.github.io/apps/settings/")
    print("\t3. Install pre-commit ci into your GitHub account to enable pre-commit hooks.")
    print("\t   https://pre-commit.ci/")
    print("Follow the rest of the instructions from cookiecutter-hypermodern-python once you have done the above.")
    print("You can skip manually creating a repository if you already used gh.")
    print("https://cookiecutter-hypermodern-python.readthedocs.io/en/2022.6.3.post1/quickstart.html#running")


if __name__ == "__main__":
    reindent_cookiecutter_json()

    print("Initializing git repository, installing Poetry dependencies, and installing pre-commit hooks...")
    print("You will probably get prompted for your GPG key passphrase, if you have one configured. "
          "If you don't have one, you should set one up!")
    git_init()
    poetry_install()
    pre_commit_install()

    print("Validating project with nox (this WILL take a while)...")
    confirm_nox_install()

    print_notices()
