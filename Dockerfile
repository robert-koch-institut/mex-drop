# syntax=docker/dockerfile:1

FROM python:3.11 as base

LABEL org.opencontainers.image.authors="RKI MEx Team <mex@rki.de>"
LABEL org.opencontainers.image.description="Data ingestion service for the MEx project."
LABEL org.opencontainers.image.licenses="MIT"

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

RUN --mount=type=cache,target=/root/.cache/pip pip install .

USER mex

EXPOSE 8081

ENTRYPOINT [ "drop" ]
