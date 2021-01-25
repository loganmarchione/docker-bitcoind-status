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
        x = r['data']['amount']
        return x
    except requests.exceptions.ConnectionError as err:
        print("ERROR: Price check error", err)
        e = "Price check error"
        return e


def supply_check() -> int:
    '''Takes no input, just return the total supply of Bitcoin in satoshis'''

    url = "https://api.blockchain.info/stats"

    try:
        print("STATE: Running supply check", url)
        r = requests.get(url).json()
        x = r['totalbc']
        return x
    except requests.exceptions.ConnectionError as err:
        print("ERROR: Price check error", err)
        e = "Supply check error"
        return e


def metric_converter(v: int, s: int) -> float:
    '''
    Takes in metric value and exponent, returns converted value

    Parameters:
        v (int):    Value (e.g., bytes)
        s (int):    Exponent (10**s)

    Returns:
        float       Converted value
    '''

    # 10**3 = kilo
    # 10**6 = mega
    # 10**9 = giga
    # 10**12 = tera
    # 10**15 = peta
    # 10**18 = exa
    x = (v / 10**s)
    return x


def conn_check():
    '''Takes no input, just runs the connection check, exit if fail'''

    print("STATE: Running connection check on", connection_string)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    q = s.connect_ex((bitcoind_host, bitcoind_port))
    if q == 0:
        print("STATE: Connection to node is OK")
    else:
        print("ERROR: Connection to node is NOT OK, check host/port, exiting")
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

    # Check the price
    price = float(price_check(currency))
    price_pretty = str("{:,}".format(price))

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
    uptime_pretty = datetime.timedelta(seconds=uptime)

    payload3 = json.dumps({"jsonrpc": "1.0", "id": "curltest", "method": "getmemoryinfo", "params": ["stats"]})
    r3 = requests.post(connection_string, data=payload3, auth=(rpc_user, rpc_pass), headers=headers)
    j3 = r3.json()
    r3.close()
    mem_used = int(j3['result']['locked']['used'])
    mem_used_pretty = round(metric_converter(mem_used, 6), 2)
    mem_total = int(j3['result']['locked']['total'])
    mem_total_pretty = round(metric_converter(mem_total ,6), 2)
    mem_perc_pretty = round(((mem_used / mem_total) * 100), 2)

    payload4 = json.dumps({"jsonrpc": "1.0", "id": "curltest", "method": "getblockchaininfo", "params": []})
    r4 = requests.post(connection_string, data=payload4, auth=(rpc_user, rpc_pass), headers=headers)
    j4 = r4.json()
    r4.close()
    chain = str(j4['result']['chain'])
    blocks = int(j4['result']['blocks'])
    blocks_pretty = str("{:,}".format(blocks))
    initial = str(j4['result']['initialblockdownload'])
    verificationprogress = float(j4['result']['verificationprogress'])
    verificationprogress_pretty = round((verificationprogress * 100), 3)
    size_on_disk = float(j4['result']['size_on_disk'])
    size_on_disk_pretty = round(metric_converter(size_on_disk, 9), 2)
    pruned = str(j4['result']['pruned'])

    payload5 = json.dumps({"jsonrpc": "1.0", "id": "curltest", "method": "getnetworkhashps", "params": [144]})
    r5 = requests.post(connection_string, data=payload5, auth=(rpc_user, rpc_pass), headers=headers)
    j5 = r5.json()
    r5.close()
    hash_rate_1_day = float(j5['result'])
    hash_rate_1_day_pretty = round(metric_converter(hash_rate_1_day, 18), 2)

    payload6 = json.dumps({"jsonrpc": "1.0", "id": "curltest", "method": "getnetworkhashps", "params": [-1]})
    r6 = requests.post(connection_string, data=payload6, auth=(rpc_user, rpc_pass), headers=headers)
    j6 = r6.json()
    r6.close()
    hash_rate_last_diff = float(j6['result'])
    hash_rate_last_diff_pretty = round(metric_converter(hash_rate_last_diff, 18), 2)

    payload7 = json.dumps({"jsonrpc": "1.0", "id": "curltest", "method": "getmininginfo", "params": []})
    r7 = requests.post(connection_string, data=payload7, auth=(rpc_user, rpc_pass), headers=headers)
    j7 = r7.json()
    r7.close()
    difficulty = float(j7['result']['difficulty'])
    difficulty_pretty = str("{:,}".format(difficulty))

    payload8 = json.dumps({"jsonrpc": "1.0", "id": "curltest", "method": "getmempoolinfo", "params": []})
    r8 = requests.post(connection_string, data=payload8, auth=(rpc_user, rpc_pass), headers=headers)
    j8 = r8.json()
    r8.close()
    mempool_size = int(j8['result']['size'])
    mempool_size_pretty = str("{:,}".format(mempool_size))
    mempool_bytes = int(j8['result']['bytes'])
    mempool_bytes_pretty = round(metric_converter(mempool_bytes, 6), 2)
    mempool_usage = int(j8['result']['usage'])
    mempool_usage_pretty = round(metric_converter(mempool_usage, 6), 2)
    mempool_max = int(j8['result']['maxmempool'])
    mempool_max_pretty = round(metric_converter(mempool_max, 6), 2)
    mempool_blocks_to_clear = int(math.trunc(metric_converter(mempool_bytes, 6)))

    payload9 = json.dumps({"jsonrpc": "1.0", "id": "curltest", "method": "getblockstats", "params": [blocks]})
    r9 = requests.post(connection_string, data=payload9, auth=(rpc_user, rpc_pass), headers=headers)
    j9 = r9.json()
    r9.close()
    subsidy = int(j9['result']['subsidy'])
    subsidy_pretty = (subsidy / 100000000)
    subsidy_currency = float(subsidy * price)
    subsidy_currency_pretty = str("{:,}".format(subsidy_currency / 100000000))
    blockhash = str(j9['result']['blockhash'])
    block_size_bytes = int(j9['result']['total_size'])
    block_size_bytes_pretty = round(metric_converter(block_size_bytes, 6), 2)

    # Values that need to be converted to look pretty on the HTML page
    sats_per_currency = int(math.trunc((100000000 / price)))
    sats_per_currency_pretty = str("{:,}".format(sats_per_currency))
    supply_sats = int(supply_check())
    supply_btc = float(supply_sats / 100000000)
    supply_pretty = str("{:,}".format(supply_btc))
    market_cap = float(price * supply_btc)
    market_cap_pretty = str("{:,}".format(round(market_cap, 2)))

    return render_template("index.html",
                           **locals(),
                           connection_string=connection_string,
                           currency=currency,
                           page_title=page_title,
                           version=version,
                           refresh=refresh_time())


if __name__ == "__main__":
    app.run(host='0.0.0.0', ssl_context='adhoc')
