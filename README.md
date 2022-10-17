# ⚠️ WARNING ⚠️

This project relies on an [API that is not reliable](https://github.com/loganmarchione/docker-bitcoind-status/issues/1). As such, I will not be updating this code.

# docker-bitcoind-status

Uses Bitcoin's RPC interface to get node data and display it in a Python Flask application
  - Source code: [GitHub](https://github.com/loganmarchione/docker-bitcoind-status)
  - Image base: [Python (slim Buster)](https://hub.docker.com/_/python)
  - Init system: N/A
  - Application: N/A
  - Architecture: `linux/amd64`

![Screenshot](https://raw.githubusercontent.com/loganmarchione/docker-bitcoind-status/master/screenshots/2021-01-19.png)

## Explanation

  - I was looking for a way to monitor my Bitcoin node from my phone, without needing to log in and tail the log files.
  - There were already a few very good existing applications, but they didn't quite meet my needs:
    * [mempool.space](https://github.com/mempool/mempool)
    * [btc-rpc-explorer](https://github.com/janoside/btc-rpc-explorer)
    *  I'm also not looking to replace [Clark Moody's dashboard](https://bitcoin.clarkmoody.com/dashboard/), since this is supposed to be about statistics on a single node
  - This project was heavily inspired by [this script](https://github.com/mameier/bitcoind-status-bash), but implemented (rather poorly) in Python, runs in Docker, and uses Bitcoin's RPC interface (to connect to remote nodes).
  - ⚠️ Bitcoin's RPC connection is not encrypted via SSL ([as-of v0.12.0](https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-0.12.0.md#rpc-ssl-support-dropped)), so do **NOT** use this over the public internet ⚠️
  - ⚠️ I would recommend **NOT** running a wallet on the node you're querying, to minimize chance of loss of funds ⚠️

## Requirements

  - You must already have a working Bitcoin node somewhere, and the ability (via the [bitcon.conf](https://github.com/bitcoin/bitcoin/blob/master/share/examples/bitcoin.conf) file) to connect to that node via the RPC interface.
  - Because of the number of RPCs required, you'll need to set `rpcworkqueue=32` (or  higher) in `bitcoin.conf`.

## Docker image information

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

#### Build

```
git clone https://github.com/loganmarchione/docker-bitcoind-status.git
cd docker-bitcoind-status
sudo docker build --no-cache --file Dockerfile --tag loganmarchione/docker-bitcoind-status  .
```

#### Run
Page will be available **only** over HTTPS at `https://YOUR_IP_ADDRESS:PORT_YOU_CHOSE` (there will be a self-signed certificate from Flask).

```
sudo docker run --name docker-bitcoind-status \
  --env BITCOIND_HOST=10.10.1.32 \
  --env BITCOIND_PORT=8332 \
  --env RPC_USER=satoshi \
  --env RPC_PASS=Bitc0inIsGreat1 \
  --env CURRENCY=USD \
  --env PAGE_TITLE="Bitcoin is great" \
  -p 5000:5000 \
  loganmarchione/docker-bitcoind-status
```

## TODO
- [ ] Learn Python
- [ ] Learn Flask
- [ ] Add a proper web server (e.g., Gunicorn, WSGI, etc...)
- [x] ~~Add a [healthcheck](https://docs.docker.com/engine/reference/builder/#healthcheck)~~
- [ ] Change request connection timeout (currently default)
- [ ] Fix error on bad node connection (should exit, but doesn't) 
- [x] ~~Add second table~~
- [x] ~~Find more elegant way to make the RPCs (maybe a function or something?)~~
- [x] ~~Add price check~~
- [ ] Add better exception handling to price check
- [ ] Find a way to get total number of BTC mined (`gettxoutsetinfo`) was too slow
- [x] ~~Add favicon~~
- [x] ~~Add SSL support~~
- [x] ~~Switch to Ubuntu-based Python image (needed for SSL support)~~
