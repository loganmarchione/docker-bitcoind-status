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

![Screenshot](screenshots/2021-01-18.png?raw=true "Screenshot")

## Explanation

  - I was looking for a way to monitor my Bitcoin node from my phone, without needing to log in and tail the log files. Products like [mempool.space](https://github.com/mempool/mempool) would work, but were too heavy for what I needed. I'm also not looking to replace [Clark Moody's dashboard](https://bitcoin.clarkmoody.com/dashboard/), since this is supposed to be about statistics on a single node.
  - This project was heavily inspired by [this script](https://github.com/mameier/bitcoind-status-bash), but implemented (rather poorly) in Python, runs in Docker, and uses Bitcoin's RPC interface (to connect to remote nodes).
  - All data is obtained from your node, **except** price data (which comes from Coinbase). CSS and icons are from external sources.
  - ⚠️ Bitcoin's RPC connection is not encrypted via SSL ([as-of v0.12.0](https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-0.12.0.md#rpc-ssl-support-dropped)), so do **NOT** use this over the public internet ⚠️
  - ⚠️ I would recomment **NOT** running a wallet on the node you're querying, to minimize chance of loss of funds ⚠️

## Requirements

  - You must already have a working Bitcoin node somewhere, and the ability (via the [bitcon.conf](https://github.com/bitcoin/bitcoin/blob/master/share/examples/bitcoin.conf) file) to connect to that node via the RPC interface.
  - Because of the number of RPCs required, you'll need to set `rpcworkqueue=32` (or  higher) in `bitcoin.conf`.

## Docker image information

### Docker image tags
  - `latest`: Latest version
  - `X.X.X`: [Semantic version](https://semver.org/) (use if you want to stick on a specific version)

### Environment variables
| Variable       | Required?                     | Definition                            | Example                                     | Comments                                           |
|----------------|-------------------------------|---------------------------------------|---------------------------------------------|----------------------------------------------------|
| BITCOIND_HOST  | No (default: localhost)       | Bitcoin node address                  | 'localhost' or your Docker service name     |                                                    |
| BITCOIND_PORT  | No (default: 8332)            | Bitcoin node                          | 8332                                        |                                                    |
| RPC_USER       | Yes                           | RPC username                          | satoshi                                     |                                                    |
| RPC_PASS       | Yes                           | RPC password                          | Bitc0inIsGreat1                             |                                                    |
| CURRENCY       | No (default: USD)             | Three-character currency code         | USD                                         | `https://api.coinbase.com/v2/currencies`           |
| PAGE_TITLE     | No (default: Bitcoind status) | HTML `<title>` tag                    | Bitcoin is great                            |                                                    |

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
      - BITCOIND_PORT=8332
      - RPC_USER=satoshi
      - RPC_PASS=Bitc0inIsGreat1
      - CURRENCY=USD
      - PAGE_TITLE=Bitcoin is great
    networks:
      - bitcoin
    ports:
      - '5000:5000'
    image: loganmarchione/docker-bitcoind-status:latest

networks:
  bitcoin:
```

## TODO
- [ ] Learn Python
- [ ] Learn Flask
- [ ] Add a proper web server (e.g., Gunicorn, WSGI, etc...)
- [x] ~~Add a [healthcheck](https://docs.docker.com/engine/reference/builder/#healthcheck)~~
- [ ] Change request connection timeout (currently default)
- [ ] Fix error on bad node connection (should exit, but doesn't) 
- [x] ~~Add second table~~
- [ ] Find more elegant way to make the RPCs (maybe a function or something?)
- [x] ~~Add price check~~
- [ ] Add better exception handling to price check
- [ ] Find a way to get total number of BTC mined (`gettxoutsetinfo`) was too slow
- [ ] Add favicon
