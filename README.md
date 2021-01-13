# docker-bitcoind-status 

![CI/CD](https://github.com/loganmarchione/docker-bitcoind-status/workflows/CI/CD/badge.svg)
[![Docker Image Size (latest semver)](https://img.shields.io/docker/image-size/loganmarchione/docker-bitcoind-status)](https://hub.docker.com/r/loganmarchione/docker-bitcoind-status)
[![MicroBadger Layers](https://img.shields.io/microbadger/layers/loganmarchione/docker-bitcoind-status)](https://microbadger.com/images/loganmarchione/docker-bitcoind-status)

Uses Bitcoin's RPC interface to get node data and display it in a Python Flask application
  - Source code: [GitHub](https://github.com/loganmarchione/docker-bitcoind-status)
  - Docker container: [Docker Hub](https://hub.docker.com/r/loganmarchione/docker-bitcoind-status)
  - Image base: [Python (Alpine)](https://hub.docker.com/_/python)
  - Init system: N/A
  - Application: N/A

## Explanation

  - Heavily inspired by [this script](https://github.com/mameier/bitcoind-status-bash), but implemented (poorly) in Python, runs in Docker, and uses Bitcoin's RPC interface (to connect to remote nodes)
  - ⚠️ Bitcoin's RPC connection is not encrypted via SSL ([as-of v0.12.0](https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-0.12.0.md#rpc-ssl-support-dropped)), so do **NOT** use this over the public internet ⚠️
  - ⚠️ I would recomment **NOT** running a wallet on the node you're querying, to minimize chance of loss of funds ⚠️

## Requirements

  - You must already have a working Bitcoin node somewhere, and the ability (via the [bitcon.conf](https://github.com/bitcoin/bitcoin/blob/master/share/examples/bitcoin.conf) file) to connect to that node via the RPC interface.

## Docker image information

### Docker image tags
  - `latest`: Latest version
  - `X.X.X`: [Semantic version](https://semver.org/) (use if you want to stick on a specific version)

### Environment variables
| Variable       | Required?                  | Definition                                     | Example                                     | Comments                                                                                         |
|----------------|----------------------------|------------------------------------------------|---------------------------------------------|--------------------------------------------------------------------------------------------------|
| BITCOIND_HOST  | No (default: localhost)    | Bitcoin node address                           | 'localhost' or your Docker service name     |                                                                                                  |
| BITCOIND_PORT  | No (default: 8086)         | Bitcoin node                                   | 8086                                        |                                                                                                  |
| RPC_USER       | Yes                        | RPC username                                   | satoshi                                     |                                                                                                  |
| RPC_PASS       | Yes                        | RPC password                                   | Bitco0nIsGreat1                             |                                                                                                  |

### Ports
| Port on host              | Port in container | Comments              |
|---------------------------|-------------------|-----------------------|
| Choose at your discretion | 5000              | Flask (web interface) |

### Volumes
N/A

### Example usage
Below is an example docker-compose.yml file.
```
version: '3'
services:
  docker-bitcoind-status:
    container_name: docker-bitcoind-status
    restart: unless-stopped
    environment:
      - BITCOIND_HOST=10.10.1.4
      - BITCOIND_PORT=8086
      - RPC_USER=satoshi
      - RPC_PASS=Bitco0nIsGreat1
    networks:
      - bitcoin
    image: loganmarchione/docker-bitcoind-status:latest

networks:
  bitcoin:
```

## TODO
- [ ] Learn Python
- [ ] Learn Flask
- [ ] Add a proper web server (e.g., Gunicorn, WSGI, etc...)
- [ ] Add a [healthcheck](https://docs.docker.com/engine/reference/builder/#healthcheck)
- [ ] Change connection timeout (currently default)
- [ ] Fix error on bad node connection (should exit, but doesn't) 
