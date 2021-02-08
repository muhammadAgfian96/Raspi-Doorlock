#
#  Lazy Pirate client
#  Use zmq_poll to do a safe request-reply
#  To run, start lpserver and then randomly kill/restart it
#
#   Author: Daniel Lundin <dln(at)eintr(dot)org>
#
# https://zguide.zeromq.org/docs/chapter4/
import sys
sys.path.append('../') 
import itertools
import logging
import sys
import zmq
import ast
import time
import raspi_handler as rpi
from config import get_configs

conf = get_configs()
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

conf.zmq.REQUEST_TIMEOUT = 5000
conf.zmq.REQUEST_RETRIES = 3
conf.zmq.SERVER_ENDPOINT = "tcp://localhost:5555"

context = zmq.Context()

logging.info("Connecting to server…")
client = context.socket(zmq.REQ)
client.connect(conf.zmq.SERVER_ENDPOINT)


def send_request(data = {}, topic='0'):
    '''
    this is receive just one face
    data = {
            'bbox': [],
            'id' : ***
        }
    '''
    my_data = {
            'device_id': topic,
            'data': data,
        }
    request = str(my_data).encode()
    logging.info("Sending (%s)", request)
    client.send(request)


def processingReply(replay):
    dict_name = {}
    list_pred_name, list_bboxes = reply['names'], reply['bboxes']
    for regonized_name, single_bbox in zip(list_pred_name, list_bboxes):
            id_name = int(np.array(single_bbox).sum())

            if regonized_name.lower() == "unknown":
                #socket.send(b"High")
                print("Unknown, Not Open")
                rpi.open_status_face = False
            elif regonized_name.lower() != "unknown":
                rpi.open_status_face = True
                dict_name[id_name] = regonized_name
    
    rpi.main_output()
    return list_bboxes, dict_name


def waiting_reply():
    '''
    @return:
        - replay = {
            "topic": str(self.topic),
            "bboxes" : [[bbox1], [bbox2], ... , [bbox3]],
            "names" : [[name1], [name2], ... ,[name3]],
            "acc"  : [[acc1], [acc2], ... ,[acc3]],
            "time" : now
        }

    '''
    retries_left = conf.zmq.REQUEST_RETRIES
    reply = {}

    while True:
        if (client.poll(conf.zmq.REQUEST_TIMEOUT) & zmq.POLLIN) != 0:
            reply = client.recv(flags=zmq.NOBLOCK)
            reply = ast.literal_eval(reply.decode('utf-8'))
            list_bboxes, dict_name = processingReply(reply)
            # print("[REPLY]",reply, type(reply))
            # logging.info("Server replied OK (%s)", reply)
            return list_bboxes, dict_name

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
        client.connect(conf.zmq.SERVER_ENDPOINT)
        logging.info("Resending (%s)", request)
        client.send(request)

    return [], {}


# for sequence in itertools.count():
#     time.sleep(2)
#     send_req(client)
#     reply = waiting_reply(client)
#     logging.info("[LUAR] Server replied OK (%s)", reply)
