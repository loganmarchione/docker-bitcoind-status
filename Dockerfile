FROM python:3.8-slim-bullseye

ARG BUILD_DATE

LABEL \
  maintainer="Logan Marchione <logan@loganmarchione.com>" \
  org.opencontainers.image.authors="Logan Marchione <logan@loganmarchione.com>" \
  org.opencontainers.image.title="docker-bitcoind-status" \
  org.opencontainers.image.description="Uses Bitcoin's RPC interface to get node data and display it in a Python Flask application" \
  org.opencontainers.image.created=$BUILD_DATE

RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat && \
    rm -rf /var/lib/apt/lists/* && \
    adduser --system status

USER status

WORKDIR /usr/scr/app

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD ["python", "-u", "./status.py"]

HEALTHCHECK CMD nc -z localhost 5000 || exit 1
