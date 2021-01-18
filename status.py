#!/usr/bin/env python3

import datetime
import json
import os
import requests
import socket
import sys
from prettytable import PrettyTable
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


def price_check(c: str) -> int:
    '''
    Takes in currency code, returns Bitcoin price

    Parameters:
        c (str):    Currency code from Coinbase https://api.coinbase.com/v2/currencies

    Returns:
        int         Bitcoin price in that currency
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


def build_table1() -> str:
    '''Takes no input, just builds the table and output HTML'''

    # First, check the connection
    conn_check()

    # RPC calls to get info
    headers = {'content-type': 'text/plain'}
    payload1 = json.dumps({"jsonrpc": "1.0", "id": "curltest", "method": "getnetworkinfo", "params": []})
    r1 = requests.post(connection_string, data=payload1, auth=(rpc_user, rpc_pass), headers=headers)
    j1 = r1.json()
    r1.close()

    payload2 = json.dumps({"jsonrpc": "1.0", "id": "curltest", "method": "uptime", "params": []})
    r2 = requests.post(connection_string, data=payload2, auth=(rpc_user, rpc_pass), headers=headers)
    j2 = r2.json()
    r2.close()

    payload3 = json.dumps({"jsonrpc": "1.0", "id": "curltest", "method": "getmemoryinfo", "params": ["stats"]})
    r3 = requests.post(connection_string, data=payload3, auth=(rpc_user, rpc_pass), headers=headers)
    j3 = r3.json()
    r3.close()

    # Save the responses to variables
    subversion = str(j1['result']['subversion'])
    connections = int(j1['result']['connections'])
    uptime = int(j2['result'])
    mem_used = int(j3['result']['locked']['used'])
    mem_free = int(j3['result']['locked']['free'])  # noqa: F841
    mem_total = int(j3['result']['locked']['total'])
    mem_perc = round(((mem_used/mem_total) * 100), 2)

    # Here we assemble the table
    x = PrettyTable()
    x.field_names = ["Name", "Value"]
    x.align = "l"
    x.add_rows(
        [
            ["Node address", connection_string],
            ["Client version", subversion.strip('/')],
            ["Connections", connections],
            ["Uptime (days, hour:min:sec)", datetime.timedelta(seconds=uptime)],
            ["Memory", "Used: " + str(round((mem_used / 1000), 2)) + " MB of  Total: " + str(round((mem_total / 1000), 2)) + " MB (" + str(mem_perc) + "% used)"]
        ]
    )
    html = x.get_html_string(attributes={"class": "table is-bordered is-striped is-hoverable"})
    return html


def build_table2() -> str:
    '''Takes no input, just builds the table and output HTML'''

    # First, check the connection
    conn_check()

    # RPC calls to get info
    headers = {'content-type': 'text/plain'}
    payload1 = json.dumps({"jsonrpc": "1.0", "id": "curltest", "method": "getblockchaininfo", "params": []})
    r1 = requests.post(connection_string, data=payload1, auth=(rpc_user, rpc_pass), headers=headers)
    j1 = r1.json()
    r1.close()

    # Save the responses to variables
    chain = str(j1['result']['chain'])
    blocks = int(j1['result']['blocks'])
    initial = str(j1['result']['initialblockdownload'])
    difficulty = float(j1['result']['difficulty'])
    verificationprogress = float(j1['result']['verificationprogress'])
    size_on_disk = float(j1['result']['size_on_disk'])
    pruned = str(j1['result']['pruned'])

    # Here we assemble the table
    x = PrettyTable()
    x.field_names = ["Name", "Value"]
    x.align = "l"
    x.add_rows(
        [
            ["Chain", chain],
            ["Block number", blocks],
            ["Initial block download?", initial],
            ["Difficulty", difficulty],
            ["Verification", verificationprogress],
            ["Size on disk", str(round((size_on_disk / 1000 / 1000 / 1000), 2)) + " GB"],
            ["Is pruned?", pruned]
        ]
    )
    html = x.get_html_string(attributes={"class": "table is-bordered is-striped is-hoverable"})
    return html


def build_table3() -> str:
    '''Takes no input, just builds the table and output HTML'''

    # First, check the connection
    conn_check()

    # RPC calls to get info
    headers = {'content-type': 'text/plain'}
    payload1 = json.dumps({"jsonrpc": "1.0", "id": "curltest", "method": "getnetworkhashps", "params": []})
    r1 = requests.post(connection_string, data=payload1, auth=(rpc_user, rpc_pass), headers=headers)
    j1 = r1.json()
    r1.close()

    payload2 = json.dumps({"jsonrpc": "1.0", "id": "curltest", "method": "getnetworkhashps", "params": [-1]})
    r2 = requests.post(connection_string, data=payload2, auth=(rpc_user, rpc_pass), headers=headers)
    j2 = r2.json()
    r2.close()

    # Save the responses to variables
    hash_rate = float(j1['result'])
    hash_rate_last_diff = float(j2['result'])

    # Here we assemble the table
    x = PrettyTable()
    x.field_names = ["Name", "Value"]
    x.align = "l"
    x.add_rows(
        [
            ["Estimated hash rate", str(round(hash_to_hash(hash_rate), 2)) + " EH/s"],
            ["Estimated hash rate (since last difficulty adjustment)", str(round(hash_to_hash(hash_rate_last_diff), 2)) + " EH/s"]
        ]
    )
    html = x.get_html_string(attributes={"class": "table is-bordered is-striped is-hoverable"})
    return html


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
    return render_template("index.html", table1=build_table1(), table2=build_table2(), table3=build_table3(), version=version, currency=currency, price=price_check(currency), refresh=refresh_time(), title=page_title)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
