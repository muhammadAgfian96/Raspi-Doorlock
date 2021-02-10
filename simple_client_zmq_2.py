#
#  Lazy Pirate client
#  Use zmq_poll to do a safe request-reply
#  To run, start lpserver and then randomly kill/restart it
#
#   Author: Daniel Lundin <dln(at)eintr(dot)org>
#
# https://zguide.zeromq.org/docs/chapter4/

import itertools
import logging
import sys
import zmq
import ast
import time

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

REQUEST_TIMEOUT = 3000
REQUEST_RETRIES = 3
SERVER_ENDPOINT = "tcp://localhost:5555"

context = zmq.Context()

logging.info("Connecting to server…")
client = context.socket(zmq.REQ)
client.connect(SERVER_ENDPOINT)

request = None
def send_req(client):
    global request
    my_data = {
            'device_id': "0",
            'hello': "1 ini dari raspi-1"
        }
    request = str(my_data).encode()
    logging.info("[SENDING] (%s)", request)
    client.send(request)

def waiting_reply(client, hasSend):
    global request
    retries_left = REQUEST_RETRIES
    hasReceive = False
    reply = {}

    print('process...')

    try:
        reply = client.recv(flags=zmq.NOBLOCK)
        
        reply = ast.literal_eval(reply.decode('utf-8'))
        print("[REPLY]",reply, type(reply))
        logging.info("Server replied OK (%s)", reply)
        # continue
        hasSend = False
        hasReceive = True
    except:
    # else:
        print('no reply')
    #     client.setsockopt(zmq.LINGER, 0)
    #     client.close()
        
        if hasReceive:
            hasSend = True
        break
    # print('heheh works')
    # retries_left -= 1
    # logging.warning("No response from server")

    # Socket is confused. Close and remove it.
    # if retries_left == 0:
    #     logging.error("Server seems to be offline, abandoning")
    #     retries_left = 3
    #     continue

    # logging.info("Reconnecting to server…")
    # # Create new connection
    # client = context.socket(zmq.REQ)
    # client.connect(SERVER_ENDPOINT)
    # logging.info("Resending (%s)", request)
    # client.send(request)
    return reply, hasSend, hasReceive

hasSend = False
for sequence in itertools.count():
    print('wait 2 seconds...', hasSend)
    time.sleep(2)

    if not hasSend:
        send_req(client)
        hasSend = True
    reply = waiting_reply(client,hasSend)
    # logging.info("[LUAR] Server replied OK (%s)", reply)
