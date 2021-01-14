FROM python:3.7-alpine

ARG BUILD_DATE

LABEL \
  maintainer="Logan Marchione <logan@loganmarchione.com>" \
  org.opencontainers.image.authors="Logan Marchione <logan@loganmarchione.com>" \
  org.opencontainers.image.title="docker-bitcoind-status" \
  org.opencontainers.image.description="Uses Bitcoin's RPC interface to get node data and display it in a Python Flask application" \
  org.opencontainers.image.created=$BUILD_DATE

RUN adduser --system status

USER status

WORKDIR /usr/scr/app

COPY requirements.txt .

COPY status.py .

COPY VERSION .

COPY templates templates/

RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD ["python", "-u", "./status.py"]
