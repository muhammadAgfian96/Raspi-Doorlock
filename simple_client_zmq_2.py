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

REQUEST_TIMEOUT = 5000
REQUEST_RETRIES = 3
SERVER_ENDPOINT = "tcp://localhost:5555"

context = zmq.Context()

logging.info("Connecting to server…")
client = context.socket(zmq.REQ)
client.connect(SERVER_ENDPOINT)


def send_req(client):
    my_data = {
            'device_id': "0",
            'hello': "1 ini dari raspi-1"
        }
    request = str(my_data).encode()
    logging.info("Sending (%s)", request)
    client.send(request)

def waiting_reply(client):

    retries_left = REQUEST_RETRIES
    reply = {}
    while True:
        if (client.poll(REQUEST_TIMEOUT) & zmq.POLLIN) != 0:
            reply = client.recv(flags=zmq.NOBLOCK)
            reply = ast.literal_eval(reply.decode('utf-8'))
            print("[REPLY]",reply, type(reply))
            logging.info("Server replied OK (%s)", reply)
            break
        
        print('heheh works')
        retries_left -= 1
        logging.warning("No response from server")

        # Socket is confused. Close and remove it.
        client.setsockopt(zmq.LINGER, 0)
        client.close()
        if retries_left == 0:
            logging.error("Server seems to be offline, abandoning")
            sys.exit()

        logging.info("Reconnecting to server…")
        # Create new connection
        client = context.socket(zmq.REQ)
        client.connect(SERVER_ENDPOINT)
        logging.info("Resending (%s)", request)
        client.send(request)
    return reply


for sequence in itertools.count():
    time.sleep(2)
    send_req(client)
    reply = waiting_reply(client)
    logging.info("[LUAR] Server replied OK (%s)", reply)
