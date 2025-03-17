# syntax=docker/dockerfile:1
FROM ubuntu:22.04
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/


# install build dependencies

RUN --mount=type=cache,target=/var/lib/apt,sharing=locked --mount=type=cache,target=/var/cache/apt,sharing=locked \
    apt-get update -y && apt-get install --no-install-recommends -y \
    python3-pip python3 locales python3-venv curl \
    && apt-get clean && rm -f /var/lib/apt/lists/*_*

# Set the locale
RUN echo 'en_US.UTF-8 UTF-8' >>/etc/locale.gen && locale-gen

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8
ENV UV_LINK_MODE=copy
ENV UV_CACHE_DIR=/opt/uv-cache

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt


# Venv by default in .venv (as per uv)
RUN uv venv --python 3.10
RUN --mount=type=cache,target=/opt/uv-cache VIRTUAL_ENV=env uv pip install --upgrade -r requirements.txt

COPY ./app /code/app
COPY ./log_conf.yaml ./

CMD ["uv","run", "uvicorn",  "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "log_conf.yaml"]
