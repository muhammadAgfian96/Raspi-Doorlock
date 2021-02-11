import sys
from easydict import EasyDict as edict 
import cv2
import numpy as np

def load_image_to_screen(path_img):
    image = cv2.imread(path_img)
    image = cv2.resize(image, (512,512))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


def get_configs(**kwargs):
    conf = edict()

    # addres server
    conf.addr = {}
    conf.addr.server =  '169.254.250.92'
    conf.addr.tcp_server = f'tcp://{conf.addr.server}:5556'
    conf.addr.raspi = '169.254.85.183'

    # zmq handler
    conf.zmq = {}
    conf.zmq.REQUEST_TIMEOUT = 500
    conf.zmq.REQUEST_RETRIES = 3
    conf.zmq.SERVER_ENDPOINT = conf.addr.tcp_server

    # database server
    conf.db = {}
    conf.db.host = conf.addr.server
    conf.db.port = 3306
    conf.db.database = ''
    conf.db.user = 'root'
    conf.db.password = 'Root@123'
    
    # camera
    conf.cam = {}
    conf.cam.raspi = f'http://{conf.addr.raspi}:8555'
    conf.cam.cctv_1 = 'rtsp://admin:aiti12345@11.11.11.81:554/Streaming/channels/101'

    # setup doorlock
    conf.doorlock = {}
    conf.doorlock.name = 'Kamar A1.6'
    conf.doorlock.topic_filter = 'pi-depan'
    conf.doorlock.months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 
                            'Jun', 'Jul', 'Aug', 'Okt', 'Sep',
                            'Nov', 'Dec']
    # conf.doorlock.waiting_image = load_image_to_screen('screen_saver.jpg')
    # conf.doorlock.too_far_image = load_image_to_screen('too_far.jpg')

    # debugging
    conf.debug = {}
    conf.debug.logging = True
    conf.debug.print = True
    conf.debug.calibration = False

    # variabel global
    conf.var = {}
    conf.var.imageThermal = np.zeros((400,300,3))

    return conf