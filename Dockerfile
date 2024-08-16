# syntax=docker/dockerfile:1

FROM python:3.11 AS base

LABEL org.opencontainers.image.authors="mex@rki.de"
LABEL org.opencontainers.image.description="Data upload and download API for the MEx project."
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.url="https://github.com/robert-koch-institut/mex-drop"
LABEL org.opencontainers.image.vendor="robert-koch-institut"

ENV PYTHONUNBUFFERED=1
ENV PYTHONOPTIMIZE=1

ENV PIP_PROGRESS_BAR=off
ENV PIP_PREFER_BINARY=on
ENV PIP_DISABLE_PIP_VERSION_CHECK=on

ENV MEX_DROP_HOST=0.0.0.0

WORKDIR /app

RUN adduser \
    --disabled-password \
    --gecos "" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "10001" \
    mex

COPY . .

RUN --mount=type=cache,target=/root/.cache/pip pip install -r locked-requirements.txt --no-deps

USER mex

EXPOSE 8081

ENTRYPOINT [ "drop" ]
