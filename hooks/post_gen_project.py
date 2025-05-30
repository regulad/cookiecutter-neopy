#!/usr/bin/env python
import json
import shutil
import subprocess
import sys
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


def get_cwd_absolute():
    return Path(".").resolve(strict=True)


def get_cookiecutter_data():
    path = Path(".cookiecutter.json")

    with path.open() as io:
        data = json.load(io)

    return data


def get_if_verification_required():
    return bool(get_cookiecutter_data().get("enforce_checks_on_creation", False))


def get_if_should_use_git():
    return bool(get_cookiecutter_data().get("initialize_git", True))


def remove_git_related_files():
    """
    Removes git related files from the project.
    """
    # We can't use rm, we may be on windows
    # Stuff like .gitignore can stay because we could be in a monorepo
    paths = [
        Path(".pre-commit-config.yaml"),
        Path(".github")
    ]

    for path in paths:
        if path.exists():
            if path.is_file():
                path.unlink()
            else:
                shutil.rmtree(path)


def git_init():
    """
    Initializes the repository with git.
    """
    subprocess.run(["git", "init", "-q", "-b", "master"], check=True, stdin=subprocess.DEVNULL)
    subprocess.run(["git", "add", "."], check=True,stdin=subprocess.DEVNULL)
    subprocess.run(["git", "commit", "-m", "initial commit"], check=True,stdin=subprocess.DEVNULL)


def poetry_install():
    """
    Installs the project with Poetry.
    """
    subprocess.run(["poetry", "--no-ansi", "-n", "lock"], check=True, stdin=subprocess.DEVNULL, cwd=get_cwd_absolute())
    subprocess.run(["poetry", "--no-ansi", "-n", "install"], check=True, stdin=subprocess.DEVNULL, cwd=get_cwd_absolute())


def pre_commit_install():
    """
    Installs pre-commit into the repository.
    """
    subprocess.run(["poetry", "--no-ansi", "-n", "run", "pre-commit", "install"], check=True, stderr=sys.stderr, 
                   stdin=subprocess.DEVNULL)


def confirm_nox_install():
    """
    Confirms that nox is installed and operating correctly.
    """

    args = [
        "poetry",
        "--no-ansi",
        "-n",
        "run",
        "nox",
    ]

    if get_if_verification_required():
        args.append("-x")

    args.extend([
        "--error-on-missing-interpreters",
        "--error-on-external-run",
        "--non-interactive",
        "-k", "not safety and not docs",  # internet connection not guaranteed
    ])

    try:
        subprocess.run(
            args,
            check=True,
            stdin=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        print("Nox is not installed or is not operating correctly. "
              "Please follow cookiecutter-neopy's instructions to install it.")
        if get_if_verification_required():
            raise
        else:
            print("Continuing without nox verification.")


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
    print("\t3. Your first CI runs will fail. This is normal. Follow all of the directions and then rerun them.")
    print("Follow the rest of the instructions from cookiecutter-hypermodern-python once you have done the above.")
    print("https://cookiecutter-hypermodern-python.readthedocs.io/en/2022.6.3.post1/quickstart.html#running")


if __name__ == "__main__":
    reindent_cookiecutter_json()

    if get_if_should_use_git():
        print("Initializing git repository, installing Poetry dependencies, and installing pre-commit hooks...")
        print("You will probably get prompted for your GPG key passphrase, if you have one configured. "
              "If you don't have one, you should set one up!")
        git_init()
    else:
        print("Installing Poetry dependencies w/o git repository initialization...")
        remove_git_related_files()
    poetry_install()
    if get_if_verification_required():
        pre_commit_install()

    print("Validating project with nox (this WILL take a while)...")
    confirm_nox_install()

    print_notices()
