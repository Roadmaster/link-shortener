# syntax=docker/dockerfile:1
FROM ubuntu:24.04
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/


# install build dependencies

RUN --mount=type=cache,target=/var/lib/apt,sharing=locked --mount=type=cache,target=/var/cache/apt,sharing=locked \
    apt-get update -y && apt-get install --no-install-recommends -y \
    python3 locales curl \
    && apt-get clean && rm -f /var/lib/apt/lists/*_*

# Set the locale
RUN echo 'en_US.UTF-8 UTF-8' >>/etc/locale.gen && locale-gen

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8
ENV UV_LINK_MODE=copy
ENV UV_CACHE_DIR=/opt/uv-cache

# Copy uv here because if uv changes it busts our base ubuntu image with packages
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /code


COPY ./pyproject.toml /code/pyproject.toml
COPY ./uv.lock /code/uv.lock

RUN --mount=type=cache,target=/opt/uv-cache uv sync --no-group dev --frozen --compile-bytecode

COPY ./app /code/app
COPY ./log_conf.yaml ./

# Empty host enables dual-stack support in uvicorn
CMD ["uv","run", "--no-group", "dev", "uvicorn",  "app.main:app", "--host", "", "--port", "8000", "--log-config", "log_conf.yaml"]
