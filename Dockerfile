# syntax=docker/dockerfile:1@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e

FROM python:3.14@sha256:12d187a59ecdeb95df0a78cd6107a84398455365a66cc2183db2be42b6067d33 AS builder

WORKDIR /build

ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_NO_INPUT=on
ENV PIP_PREFER_BINARY=on
ENV PIP_PROGRESS_BAR=off

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN uv export --no-dev --no-editable | uv pip install --system --no-deps -r -

# pre-build the frontend for serving on `/` and on `/drop`, using a placeholder for
# the api url that is replaced at runtime (see `mex/drop/frontend.py`),
# the root build uses an empty frontend path, because `/` breaks the vite base url
ENV REFLEX_API_URL=http://mex-api-url-placeholder
RUN REFLEX_FRONTEND_PATH= reflex export --frontend-only --no-zip --no-ssr \
    && mkdir dist \
    && mv .web/build/client dist/root \
    && rm -rf .web
RUN REFLEX_FRONTEND_PATH=/drop reflex export --frontend-only --no-zip --no-ssr \
    && mv .web/build/client dist/drop \
    && rm -rf .web

FROM python:3.14-slim@sha256:a2b82f3c48559aa0a8446d9af49826b6e2b2016f4cd2afabfe6013ec53729170

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
