#!/usr/bin/env python3

import datetime
import json
import os
import requests
import socket
import sys
import time
from prettytable import PrettyTable
from flask import Flask, render_template

# Variables
bitcoind_host = os.getenv("BITCOIND_HOST", "localhost")
bitcoind_port = int(os.getenv("BITCOIND_PORT", 8332))
rpc_user = os.getenv("RPC_USER")
rpc_pass = os.getenv("RPC_PASS")
connection_string = "http://" + bitcoind_host + ":" + str(bitcoind_port)
start_time = datetime.datetime.utcnow().isoformat()

def conn_check():
    ''' Takes no input, just runs the connection check, exit if fail'''

    print("STATE: Running connection check on", connection_string)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    q = s.connect_ex((bitcoind_host, bitcoind_port))
    if q == 0:
        print("STATE: Connection is OK")
    else:
        print("ERROR: Connection is NOT OK, check host/port, exiting")
        sys.exit(1)


def build_table() -> str:
    '''Takes no input, just builds the table'''

    # First, check the connection
    conn_check()

    # Need two different API calls to get info
    headers = {'content-type': 'text/plain'}
    payload1 = json.dumps({"jsonrpc": "1.0", "id":"curltest", "method": "getblockchaininfo", "params": [] })
    payload2 = json.dumps({"jsonrpc": "1.0", "id":"curltest", "method": "getconnectioncount", "params": [] })
    
    # Make the requests
    r1 = requests.post(connection_string, data=payload1, auth=(rpc_user, rpc_pass), headers=headers)
    s1 = r1.status_code
    my_json1 = r1.json()
    r2 = requests.post(connection_string, data=payload2, auth=(rpc_user, rpc_pass), headers=headers)
    s2 = r2.status_code
    my_json2 = r2.json()

    # Save that responses to variables
    chain = my_json1['result']['chain']
    blocks = my_json1['result']['blocks']
    difficulty = my_json1['result']['difficulty']
    verificationprogress = my_json1['result']['verificationprogress']
    connections = my_json2['result']

    # Here we assemble the table
    x = PrettyTable()
    x.field_names = ["Name", "Value"]
    x.align = "l" 
    x.add_rows( 
        [
            ["Node location", connection_string],
            ["Chain", chain],
            ["Connections", connections],
            ["Block number", blocks],
            ["Difficulty", difficulty],
            ["Verification", verificationprogress],
            ["Last refreshed time (UTC)", datetime.datetime.utcnow().isoformat()]
        ]
    )
    print("STATE: ASCII version of the table is below")
    print(x)
    html = x.get_html_string(attributes={"class":"table is-bordered is-striped is-hoverable is-fullwidth"})
    return html


# Some logging
print("#####\n# Container starting up!\n#####")
print("STATE: Starting at", start_time)

# Check if variables are set
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
    return render_template("index.html", message=build_table());   


if __name__ == "__main__":
    app.run(host='0.0.0.0')
