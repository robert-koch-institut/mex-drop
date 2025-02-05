# syntax=docker/dockerfile:1

FROM python:3.11 AS base

LABEL org.opencontainers.image.authors="mex@rki.de"
LABEL org.opencontainers.image.description="Data upload and download service for the MEx project."
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.url="https://github.com/robert-koch-institut/mex-drop"
LABEL org.opencontainers.image.vendor="robert-koch-institut"

ENV PYTHONUNBUFFERED=1
ENV PYTHONOPTIMIZE=1

ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_NO_INPUT=on
ENV PIP_PREFER_BINARY=on
ENV PIP_PROGRESS_BAR=off

ENV APP_NAME=mex
ENV FRONTEND_PORT=8020
ENV DEPLOY_URL=http://0.0.0.0:8020
ENV BACKEND_PORT=8021
ENV API_URL=http://0.0.0.0:8021
ENV TELEMETRY_ENABLED=False
ENV REFLEX_ENV_MODE=prod
ENV REFLEX_DIR=/app/reflex

WORKDIR /app

RUN adduser \
    --disabled-password \
    --gecos "" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "10001" \
    mex && \
    chown mex .

COPY --chown=mex . .

RUN --mount=type=cache,target=/root/.cache/pip pip install -r locked-requirements.txt --no-deps

USER mex

EXPOSE 8020
EXPOSE 8021

ENTRYPOINT [ "drop", "run" ]
