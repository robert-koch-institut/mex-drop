# syntax=docker/dockerfile:1@sha256:ecfaec9ed6d810b56388c508f4121597bfbba70d41a6dfeee4d8cad5f295fc32

FROM python:3.14@sha256:1eb6b7d4b76454b1de8317863ac3213b678c337b27e604a4e3fb70bddbb2bad7 AS builder

WORKDIR /build

ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_NO_INPUT=on
ENV PIP_PREFER_BINARY=on
ENV PIP_PROGRESS_BAR=off

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN uv export --no-dev --no-editable | uv pip install --system --no-deps -r -

# pre-build the frontend for serving on `/` and on `/drop`, using a placeholder for
# the api url that is replaced at runtime (see `mex/drop/frontend.py`)
ENV REFLEX_API_URL=http://mex-api-url-placeholder
RUN REFLEX_FRONTEND_PATH=/ reflex export --frontend-only --no-zip --no-ssr \
    && mkdir dist \
    && mv .web/build/client dist/root \
    && rm -rf .web
RUN REFLEX_FRONTEND_PATH=/drop reflex export --frontend-only --no-zip --no-ssr \
    && mv .web/build/client dist/drop \
    && rm -rf .web

FROM python:3.14-slim@sha256:f85c5697265c178cc6887276c55fe16cf3d14ca35c3df6a5eab3b360534a55d2

LABEL org.opencontainers.image.authors="mex@rki.de"
LABEL org.opencontainers.image.description="Data upload and download service for the MEx project."
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.url="https://github.com/robert-koch-institut/mex-drop"
LABEL org.opencontainers.image.vendor="robert-koch-institut"

ENV PYTHONUNBUFFERED=1
ENV PYTHONOPTIMIZE=1

ENV REFLEX_APP_NAME=mex
ENV REFLEX_FRONTEND_PORT=8020
ENV REFLEX_DEPLOY_URL=http://localhost:8020
ENV REFLEX_BACKEND_PORT=8021
ENV REFLEX_API_URL=http://localhost:8021
ENV REFLEX_TELEMETRY_ENABLED=False
ENV REFLEX_ENV_MODE=prod

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin/drop-api /usr/local/bin/drop-api
COPY --from=builder /usr/local/bin/drop-frontend /usr/local/bin/drop-frontend
COPY --from=builder --chown=10001 /build/assets assets
COPY --from=builder --chown=10001 /build/rxconfig.py rxconfig.py
COPY --from=builder --chown=10001 /build/dist dist

RUN chown 10001 /app

# create the drop directory in the image, so that a volume mounted here
# inherits its ownership instead of being created as root
RUN mkdir --parents /app/data && chown 10001 /app/data

USER 10001

EXPOSE 8020
EXPOSE 8021

ENTRYPOINT [ "drop-frontend" ]
