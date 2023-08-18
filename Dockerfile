FROM python:3.11

ARG GIT_REV=main

LABEL version=${GIT_REV}
LABEL maintainer="RKI MEx Team <mex@rki.de>"
LABEL description="Docker image for mex-drop"

ENV MEX_DROP_HOST=0.0.0.0

RUN pip install \
    --disable-pip-version-check \
    --no-cache-dir \
    --prefer-binary \
    --progress-bar=off \
    git+https://github.com/robert-koch-institut/mex-drop.git@${GIT_REV}

ENTRYPOINT [ "drop" ]
