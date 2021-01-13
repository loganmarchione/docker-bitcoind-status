FROM python:3.7-alpine

ARG BUILD_DATE

LABEL \
  maintainer="Logan Marchione <logan@loganmarchione.com>" \
  org.opencontainers.image.authors="Logan Marchione <logan@loganmarchione.com>" \
  org.opencontainers.image.title="docker-bitcoind-status" \
  org.opencontainers.image.description="" \
  org.opencontainers.image.created=$BUILD_DATE

RUN adduser --system status

USER status

WORKDIR /usr/scr/app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY status.py .

COPY templates templates/

COPY VERSION /

EXPOSE 5000

CMD ["python", "-u", "./status.py"]
