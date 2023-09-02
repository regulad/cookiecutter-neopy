# https://stackoverflow.com/questions/53835198/integrating-python-poetry-with-docker/54763270#54763270
# Copyright (c) 2023  Parker Wahle - Licensed under MIT License (do whatever you want)

FROM python:3.11.5-alpine3.18 AS base

# In Python, the line between a compile-time and run-time dependency is blurry,
# so we play it safe by installing everything
RUN apk add -U tzdata --no-cache \
    && apk add gcc musl-dev libffi-dev openssl-dev make git curl python3-dev libpq-dev --no-cache \
    && pip install --upgrade pip

# --------------------------------------
# ---------- Copy and compile ----------
# We use a multi-stage build to reduce the size of the final image
FROM base AS builder

# Configure env variables for build/install
# ENV no longer adds a layer in new Docker versions,
# so we don't need to chain these in a single line
ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=120
ENV POETRY_VERSION=1.5.1

# Install system deps
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /code
# Although it would be very convienient to only copy the pyproject.toml file so that we can cache the dependencies,
# Poetry requires the whole project to be present in order to install the dependencies
COPY . /code

# Install with poetry
# pip install would probably work, too, but we'd have to make sure it's a recent enough pip
# Don't bother creating a virtual env -- significant performance increase
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --only main

# Build the package
RUN poetry build

# --------------------------------------
# ---------- Install & run! ------------
FROM base AS runner

# Set labels

# See https://github.com/opencontainers/image-spec/blob/master/annotations.md
LABEL name="{{cookiecutter.project_name}}"
LABEL version="{{cookiecutter.version}}"
LABEL vendor="{{cookiecutter.author}}"
LABEL org.opencontainers.image.title="{{cookiecutter.project_name}}"
LABEL org.opencontainers.image.version="{{cookiecutter.version}}"
LABEL org.opencontainers.image.url="https://github.com/{{cookiecutter.github_user}}/{{cookiecutter.project_name}}"
LABEL org.opencontainers.image.documentation="https://{{cookiecutter.project_name}}.readthedocs.io"

ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV TZ=America/New_York

ARG USERNAME={{cookiecutter.package_name}}
ARG USER_UID=1008
ARG USER_GID=$USER_UID

RUN addgroup -g $USER_GID -S $USERNAME \
    && adduser -u $USER_UID -G $USERNAME -D -S $USERNAME

# Switch to non-root user (for security)
# This makes dockerfile_lint complain, but it's fine
# dockerfile_lint - ignore
USER $USERNAME

# Install the package in the user space
COPY --from=builder /code/dist/{{cookiecutter.package_name}}-*.whl /tmp/
RUN pip install --user /tmp/{{cookiecutter.package_name}}-*.whl

# Expose our server
EXPOSE 8080/tcp

# And make sure nothing goes awry
HEALTHCHECK --interval=5s --timeout=5s --retries=3 CMD curl --fail http://localhost:8080/status/ || exit 1

# Now do something!
CMD ["python", "-O", "-m", "{{cookiecutter.package_name}}", "serve"]
