#!/usr/bin/env python3

import datetime
import json
import math
import os
import requests
import socket
import sys
from flask import Flask, render_template

# Variables
bitcoind_host = os.getenv("BITCOIND_HOST", "localhost")
bitcoind_port = int(os.getenv("BITCOIND_PORT", 8332))
connection_string = "http://" + bitcoind_host + ":" + str(bitcoind_port)
rpc_user = os.getenv("RPC_USER")
rpc_pass = os.getenv("RPC_PASS")
currency = os.getenv("CURRENCY", "USD")
page_title = os.getenv("PAGE_TITLE", "Bitcoind status")
start_time = datetime.datetime.utcnow().isoformat()

# Get version file
with open('VERSION') as f:
    version = f.readline()


def refresh_time() -> datetime:
    '''Takes no input, just return the datetime object'''

    r = datetime.datetime.utcnow().isoformat()
    return r


def price_check(c: str) -> float:
    '''
    Takes in currency code, returns Bitcoin price

    Parameters:
        c (str):    Currency code from Coinbase https://api.coinbase.com/v2/currencies

    Returns:
        float       Bitcoin price in that currency
    '''

    url = "https://api.coinbase.com/v2/prices/BTC-" + c + "/spot"

    try:
        print("STATE: Running price check", url)
        r = requests.get(url).json()
        price = r['data']['amount']
        return price
    except requests.exceptions.ConnectionError as err:
        print("ERROR: Price check error", err)
        e = "Price error"
        return e


def hash_to_hash(h: int) -> float:
    '''
    Takes in hash rate, returns converted hash rate

    Parameters:
        h (int):    Hash rate per second

    Returns:
        float       Converted hash rate per second
    '''

    #        kilo   mega   giga   tera   peta   exa
    x = (h / 1000 / 1000 / 1000 / 1000 / 1000 / 1000)
    return x


def conn_check():
    '''Takes no input, just runs the connection check, exit if fail'''

    print("STATE: Running connection check on", connection_string)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    q = s.connect_ex((bitcoind_host, bitcoind_port))
    if q == 0:
        print("STATE: Connection is OK")
    else:
        print("ERROR: Connection is NOT OK, check host/port, exiting")
        sys.exit(1)


#
# Script actually starts running here
#

# Some logging
print("#####\n# Container starting up!\n#####")
print("STATE: Starting at", start_time)

# Check if variables are set, otherwise fail
print("STATE: Checking environment variables...")
if 'RPC_USER' in os.environ:
    pass
else:
    print("ERROR: RPC_USER is not set")
    sys.exit(1)

if 'RPC_PASS' in os.environ:
    pass
else:
    print("ERROR: RPC_PASS is not set")
    sys.exit(1)


# Flask
app = Flask(__name__)


@app.route("/")
def index():

    # First, check the connection
    conn_check()

    # Headers
    headers = {'content-type': 'text/plain'}

    # RPC calls to get info
    payload1 = json.dumps({"jsonrpc": "1.0", "id": "curltest", "method": "getnetworkinfo", "params": []})
    r1 = requests.post(connection_string, data=payload1, auth=(rpc_user, rpc_pass), headers=headers)
    j1 = r1.json()
    r1.close()
    subversion = str(j1['result']['subversion']).strip('/')
    connections_total = int(j1['result']['connections'])
    connections_in = int(j1['result']['connections_in'])
    connections_out = int(j1['result']['connections_out'])

    payload2 = json.dumps({"jsonrpc": "1.0", "id": "curltest", "method": "uptime", "params": []})
    r2 = requests.post(connection_string, data=payload2, auth=(rpc_user, rpc_pass), headers=headers)
    j2 = r2.json()
    r2.close()
    uptime = int(j2['result'])

    payload3 = json.dumps({"jsonrpc": "1.0", "id": "curltest", "method": "getmemoryinfo", "params": ["stats"]})
    r3 = requests.post(connection_string, data=payload3, auth=(rpc_user, rpc_pass), headers=headers)
    j3 = r3.json()
    r3.close()
    mem_used = int(j3['result']['locked']['used'])
    mem_free = int(j3['result']['locked']['free'])  # noqa: F841
    mem_total = int(j3['result']['locked']['total'])

    payload4 = json.dumps({"jsonrpc": "1.0", "id": "curltest", "method": "getblockchaininfo", "params": []})
    r4 = requests.post(connection_string, data=payload4, auth=(rpc_user, rpc_pass), headers=headers)
    j4 = r4.json()
    r4.close()
    chain = str(j4['result']['chain'])
    blocks = int(j4['result']['blocks'])
    initial = str(j4['result']['initialblockdownload'])
    verificationprogress = float(j4['result']['verificationprogress'])
    size_on_disk = float(j4['result']['size_on_disk'])
    pruned = str(j4['result']['pruned'])

    payload5 = json.dumps({"jsonrpc": "1.0", "id": "curltest", "method": "getnetworkhashps", "params": [144]})
    r5 = requests.post(connection_string, data=payload5, auth=(rpc_user, rpc_pass), headers=headers)
    j5 = r5.json()
    r5.close()
    hash_rate_1_day = float(j5['result'])

    payload6 = json.dumps({"jsonrpc": "1.0", "id": "curltest", "method": "getnetworkhashps", "params": [-1]})
    r6 = requests.post(connection_string, data=payload6, auth=(rpc_user, rpc_pass), headers=headers)
    j6 = r6.json()
    r6.close()
    hash_rate_last_diff = float(j6['result'])

    payload7 = json.dumps({"jsonrpc": "1.0", "id": "curltest", "method": "getmininginfo", "params": []})
    r7 = requests.post(connection_string, data=payload7, auth=(rpc_user, rpc_pass), headers=headers)
    j7 = r7.json()
    r7.close()
    difficulty = float(j7['result']['difficulty'])

    payload8 = json.dumps({"jsonrpc": "1.0", "id": "curltest", "method": "getmempoolinfo", "params": []})
    r8 = requests.post(connection_string, data=payload8, auth=(rpc_user, rpc_pass), headers=headers)
    j8 = r8.json()
    r8.close()
    mempool_size = int(j8['result']['size'])
    mempool_bytes = int(j8['result']['bytes'])
    mempool_usage = int(j8['result']['usage'])
    mempool_max = int(j8['result']['maxmempool'])

    # Values that need to be converted to look pretty on the HTML page
    uptime = str(datetime.timedelta(seconds=uptime))
    mem_perc = str(round(((mem_used/mem_total) * 100), 2))
    mem_used = str(round((mem_used / 1000), 2))
    mem_total = str(round((mem_total / 1000), 2))
    size_on_disk = str(round((size_on_disk / (1000**3)), 2))
    hash_rate_1_day = str(round(hash_to_hash(hash_rate_1_day), 2))
    hash_rate_last_diff = str(round(hash_to_hash(hash_rate_last_diff), 2))
    mempool_blocks_to_clear = str(math.trunc(mempool_bytes / (1000**2)))
    mempool_bytes = str(round((mempool_bytes / (1000**2)), 2))
    mempool_usage = str(round((mempool_usage / (1000**2)), 2))
    mempool_max = str(round((mempool_max / (1000**2)), 2))

    price=float(price_check(currency))
    sats_per_currency = int(math.trunc((100000000 / price)))

    return render_template("index.html",
                           **locals(),
                           connection_string=connection_string,
                           currency=currency,
                           page_title=page_title,
                           version=version,
                           refresh=refresh_time())


if __name__ == "__main__":
    app.run(host='0.0.0.0')
