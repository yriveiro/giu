FROM ghcr.io/ironpeakservices/iron-alpine/iron-alpine:3.14.0

RUN apk add --no-cache python3 py3-pip

USER $APP_USER

RUN pip install --user giu
ENV PATH="${PATH}:/${APP_DIR}/.local/bin"

USER root

RUN $APP_DIR/post-install.sh \
    && chmod +x $APP_DIR/.local/bin/giu

USER $APP_USER
