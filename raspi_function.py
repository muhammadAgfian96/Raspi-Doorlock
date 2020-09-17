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


import RPi.GPIO as GPIO
GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering

#---- list pin pcb bolong ------
pcb_bolong = edict()
p_magnet_relay = 32 # ---- relay
p_led_relay    = 26 # 
p_trig_jarak   = 18 # ---- sensor jarak
p_echo_jarak   = 16 # 
p_exit_btn     = 8  # ---- button
p_buzzer       = 12 # ---- beep
p_RST_RFID     = 13 # ---- RFID
p_MISO_RFID    = 35 
p_MOSI_RFID    = 38
p_SCK_RFID     = 40
p_SDA_RFID     = 36
p_SDA_THERM    = 3  # ---- Thermal Cam
p_SCL_THERM    = 5


#------- init pin
exit_btn = sensors.PushButton(p_exit_btn)
beep     = sensors.BeepBuzzer(p_buzzer)
s_jarak  = sensors.Jarak(p_trig_jarak, p_echo_jarak)
relay_magnet = sensors.Relay(p_magnet_relay, name="magnet")
relay_led = sensors.Relay(p_led_relay, name="led")


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
Open_status = False
count_close = 0
old_time = time.time()
first_time = True
first_time_jarak = True
start_time = time.time()
signal_open = 0

def display(pesan):
    pass

def scalling(image, bbox):
    
    targetSize = image.shape
    originalSize = (400,300)
    scaleX = targetSize[0]/originalSize[0]
    scaleY = targetSize[1]/originalSize[1]

    bbox[0] = int(bbox[0]*scaleX)
    bbox[1] = int(bbox[1]*scaleY)
    bbox[2] = int(bbox[2]*scaleX)
    bbox[3] = int(bbox[3]*scaleY)
    return bbox

# old function -not used
def rcvMsg():
    message = socket.recv_string(flags=zmq.NOBLOCK, encoding='utf-8')
    now = datetime.now()
    print(message)
    now = now.strftime("%d/%m/%Y-%H:%M:%S")
    name = message.split(" ")[1]
    try:
        list_bbox = message.split(" ")[2].split(",")
        print(list_bbox)
        bbox = [int(nilai) if nilai!='-1' else 0 for nilai in list_bbox if (nilai !='')]
        bbox = scalling(bbox)
    except:
        bbox= None
    print(bbox)
    print("-- Received %s %s" % (message,now))
    return name, bbox

def rcvMsgJSON():
    data = socket.recv_multipart(flags=zmq.NOBLOCK)
    print(data)
    #data = json.loads(msg)
    data = json.loads(data[1])
    data = edict(data)
    print("JSON data:\n", type(data), data)
    return data.name, data.bbox
    
def main_vision():
    # no received handle, so program can running and not stuck using zmq.NOBLOCK
    global Open_status, old_time, first_time, start_time
    try:
        pred_name, pred_bbox  = rcvMsgJSON()
        print(pred_name, pred_bbox)
        
        if pred_name.lower() == "unknown":
            #socket.send(b"High")
            print("Unknown, Not Open")
            Open_status = False
            display("Silakan Hubungi Petugas")

        elif pred_name.lower() != "unknown":
            print(f"Silahkan Masuk {pred_name}!")
            Open_status = True

    except zmq.Again as e:
        # print("-- no received")
        pred_bbox = None
    
    main_output()
    if pred_bbox is None:
        return None, None
    else:
        return pred_bbox, pred_name
        

def main_input():
    global Open_status, first_time_jarak, signal_open, start_time_jarak

    # ---- exit button
    if exit_btn.isPressed:
        time.sleep(0.2)
        Open_status = True
        print("[sensors] button pressed")
    
    # ---- sensor jarak
    jarak_object =  s_jarak.detect(v=True)
    if  jarak_object < 7:
            signal_open += 1
            time.sleep(0.2)

    if signal_open == 5 :
        signal_open = 0
        Open_status = True
        first_time_jarak = True
        print("[sensors] signal open")
    print("[sensors] Openstatus ", Open_status)
    # ---- RFID


def main_output():
    global Open_status, first_time, start_time, start_time_jarak
    # Jika Pintu Tebuka
    if Open_status ==  True:
        if first_time == True:
            start_time = time.time()
            first_time = False
            print("get first time")
            
        else:
            relay_magnet.off(v=True)
            print("[unlocked] magnet still off ", time.time() - start_time)
            
        if time.time() - start_time >= 3:
            relay_magnet.on(v=True)
            print("[locked] magnet on")
            Open_status = False
            first_time = True
    print("[Actuators] Openstatus ", Open_status)