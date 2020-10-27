#--- Ref---
# written by:agfian
# https://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/patterns/pubsub.html
# https://stackoverflow.com/questions/26012132/zero-mq-socket-recv-call-is-blocking
# -----


from datetime import datetime
import zmq
from easydict import EasyDict as edict
from utils import sensors
# from utils.MFRC522.Read import read_card as RFID_read

import json
import time
from time import sleep     # Import the sleep function from the time module
import numpy as np
from config import *

import RPi.GPIO as GPIO
GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering

#---- list pin pcb  ------
pcb_bolong = edict()
p_magnet_relay = 22 # ---- relay
p_led_relay    = 26 # 
p_trig_jarak   = 18 # ---- sensor jarak
p_echo_jarak   = 16 # 
p_exit_btn     = 29 # ---- button
p_buzzer       = 12 # ---- beep
p_RST_RFID     = 13 # ---- RFID
p_MISO_RFID    = 35 
p_MOSI_RFID    = 38
p_SCK_RFID     = 40
p_SDA_RFID     = 36
p_SDA_THERM    = 3  # ---- Thermal Cam
p_SCL_THERM    = 5


#------- init pin and Sensors
exit_btn = sensors.PushButton(p_exit_btn)
beep     = sensors.BeepBuzzer(p_buzzer)
s_jarak  = sensors.Jarak(p_trig_jarak, p_echo_jarak)
relay_magnet = sensors.Relay(p_magnet_relay, name="magnet")
relay_led = sensors.Relay(p_led_relay, name="led")
my_card = sensors.Card()
thermalCam = sensors.CamTherm(alamat=0x68, ukuran_pix=60j, minTemp=24, maxTemp=34)

#------- GET FROM SERVER
addr_server = "tcp://11.11.11.11:5556"
topicfilter = "pi-depan"

#------- connection setting
context = zmq.Context()
#  Socket to talk to server
print("Connecting to server…")
#socket = context.socket(zmq.REQ)
socket = context.socket(zmq.SUB)

socket.connect(addr_server) #change this to ip-server
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter, encoding='utf-8')
# KeepAlive when connection unstable
socket.setsockopt(zmq.TCP_KEEPALIVE, 1)
socket.setsockopt(zmq.TCP_KEEPALIVE_IDLE, 300)
socket.setsockopt(zmq.TCP_KEEPALIVE_INTVL, 300)

#------- state
open_status_face = False
open_status_button = False
open_status_sJarak = False
open_status_RFID = False


count_close = 0
counting_RFID = 0
signal_open = 0

newPeople = []
dict_name = {}

first_time = True
first_time_jarak = True

old_time = time.time()
start_time = time.time()
door_time = time.time()
state_time_btn = time.time()
state_time_sJarak = time.time()


raspi_log = setup_logger(name = 'raspi', log_file = 'raspi_logs', 
                        folder_name='raspi_logs', level = logging.DEBUG,
                        removePeriodically=True, to_console=True,
                        interval=2, backupCount=5, when='h')


def display(pesan):
    pass


def rcvMsgJSON():
    """
    data from server receive a dictionary/JSON data = {
        'topic' : is filter for sending message
        'bboxes': list of list bbox
        'names' : list of name prediction
        'acc'   : list of accuracy by name
        'time'  : time to send this data
    }

    - return:
        @ array names. ex: ['name_1', 'name_2']
        @ array boxes. ex: [[1,2,3,4],[4,5,6,7]]
    """

    data = socket.recv_multipart(flags=zmq.NOBLOCK)
    data = json.loads(data[1])
    data = edict(data)
    # print("\n>>>>>>>>>>>>>\nJSON data receive:\n", type(data), data,'\n>>>>>>>>>>>>>\\n')
    raspi_log.info(f'[rcvMsgJSON] data receive: {type(data)}, {data} \n')
    return data.names, data.bboxes
    

def main_vision():
    # no received handle, so program can running and not stuck using zmq.NOBLOCK
    global open_status_face, open_status_button, open_status_RFID, open_status_sJarak
    global old_time, first_time, start_time, newPeople

    list_bboxes = []
    statusNewPeople = False

    try:
        dict_name = {}
        list_pred_name, list_bboxes  = rcvMsgJSON()

        for regonized_name, single_bbox in zip(list_pred_name, list_bboxes):
            id_name = int(np.array(single_bbox).sum())
            
            if regonized_name not in newPeople:
                statusNewPeople = True

            if regonized_name.lower() == "unknown":
                #socket.send(b"High")
                print("Unknown, Not Open")
                open_status_face = False
                display("Silakan Hubungi Petugas")

            elif regonized_name.lower() != "unknown":
                open_status_face = True
                dict_name[id_name] = regonized_name
                newPeople.append(regonized_name)

    except zmq.Again as e:  
        # print("-- no received")
        list_bboxes = []
    
    main_output()
    if len(list_bboxes) == 0:
        return None, None, statusNewPeople
    else:
        raspi_log.debug(f"[main_vision] dict_name: {dict_name}\n")
        return list_bboxes, dict_name, statusNewPeople
        

def main_input():
    global first_time_jarak, signal_open, start_time_jarak
    global open_status_face, open_status_button, open_status_RFID, open_status_sJarak
    global counting_RFID
    global state_time_btn, state_time_sJarak

    # ---- exit button
    if exit_btn.isPressed and (time.time() - state_time_btn > 0.1):
        # time.sleep(0.1)
        open_status_button = True
        state_time_btn = time.time()
    
    # ---- sensor jarak
    jarak_object =  s_jarak.detect(v=True)
    if  jarak_object > 3 and jarak_object < 7 and (time.time() - state_time_sJarak > 0.2):
        signal_open += 1
        state_time_sJarak = time.time()

    if signal_open == 5 :
        signal_open = 0
        open_status_sJarak = True
        first_time_jarak = True
        raspi_log.info(f"[s_jarak] {jarak_object} cm")


    # ---- RFID
    counting_RFID += 1
    if counting_RFID == 10:
        counting_RFID = 0
        uid = my_card.read_card()
        # print("[RFID CARD]", uid)
        if uid == "249108142":
            open_status_RFID = True
            raspi_log.info(f'[main_input] RFID Card: {uid}')


def main_output():
    global open_status_face, open_status_button, open_status_RFID, open_status_sJarak
    global first_time, door_time
    
    hasil = open_status_face or open_status_button or open_status_RFID or open_status_sJarak
    # Jika Pintu Tebuka
    if hasil ==  True:
        if open_status_face:
            # print('[ON] by FACE')
            raspi_log.info(f'[main_output] Relay ON by FACE')
        if open_status_sJarak:
            # print('[ON] by s JARAK')
            raspi_log.info(f'[main_output] Relay ON by s JARAK')
        if open_status_button:
            # print('[ON] by BUTTON')
            raspi_log.info(f'[main_output] Relay ON by BUTTON')
        if open_status_RFID:
            # print('[ON] by RFID')
            raspi_log.info(f'[main_output] Relay ON by RFID')

        if first_time == True:
            door_time = time.time()
            first_time = False
            # print("get first time")
            
        else:
            if time.time() - door_time >= 3:
                relay_magnet.on(v=True) # open the door
                open_status_face = open_status_button = open_status_RFID = open_status_sJarak =False
                first_time = True
            else:
                relay_magnet.off(v=True)
                
        raspi_log.info(f'[main_output] the door is open? {hasil}')
    # print("[Actuators] The Door is Open? ", hasil)
