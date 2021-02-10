#
#  Lazy Pirate client
#  Use zmq_poll to do a safe request-reply
#  To run, start lpserver and then randomly kill/restart it
#
#   Author: Daniel Lundin <dln(at)eintr(dot)org>
#
# https://zguide.zeromq.org/docs/chapter4/
import sys
sys.path.append('modules')
import itertools
import logging
import sys
import zmq
import ast
import time
import raspi_handler as rpi
from config import get_configs

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


class ZMQ_handler:
    def __init__(self):
        self.conf = get_configs()
        self.context = zmq.Context()
        logging.info("Connecting to server…")
        self.client = self.context.socket(zmq.REQ)
        self.client.connect(self.conf.zmq.SERVER_ENDPOINT)
        self.retries_left = self.conf.zmq.REQUEST_RETRIES
        self.hasReceive = False
        self.hasSend = False

    def send_request(self, data = {}, topic=''):
        '''
        this is receive just one face
        data = {
                'bbox': [],
                'id' : ***
            }
        '''
        if self.hasSend: 
            # jika sudah dikirim...
            print('sudah dikirim')
        else: 
            # jika belum dikirim
            self.my_data = {
                    'device_id': topic,
                    'data': data,
                }
            self.request = str(self.my_data).encode()
            self.client.send(self.request)
            logging.info("Sending (%s)", self.request)
            self.hasSend = True
            self.hasReceive = False

    def processingReply(self, reply):
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


    def waiting_reply(self):
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
        reply = {}
        list_bboxes, dict_name = [], {}
        self.hasReceive = False
        # if (self.client.poll(self.conf.zmq.REQUEST_TIMEOUT) & zmq.POLLIN) != 0:
        try:
            reply = self.client.recv(flags=zmq.NOBLOCK)
            reply = ast.literal_eval(reply.decode('utf-8'))
            list_bboxes, dict_name = self.processingReply(reply)
            logging.info("Server replied OK (%s)", reply)
            self.hasReceive = True
            self.hasSend = False
            self.request = None
        except:
            self.hasReceive = False
            if self.hasSend:
                self.retries_left -= 1
                logging.warning("No response from server")


        return list_bboxes, dict_name


    def reconnecting(self):

        if self.retries_left < 0:
            self.retries_left = 0
            self.hasReceive = False
            self.hasSend = False
        
        if self.request is not None and self.hasReceive == False and self.retries_left == 0:

            # Socket is self.confused. Close and remove it.
            self.client.setsockopt(zmq.LINGER, 0)
            self.client.close()

            logging.info("Reconnecting to server…")
            # Create new connection
            self.client = self.context.socket(zmq.REQ)
            self.client.connect(self.conf.zmq.SERVER_ENDPOINT)
            logging.info("Resending (%s)", self.request)
            self.client.send(self.request)

            self.retries_left = self.conf.zmq.REQUEST_RETRIES

