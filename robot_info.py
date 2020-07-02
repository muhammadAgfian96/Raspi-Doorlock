#--- Ref---
# written by:agfian
# https://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/patterns/pubsub.html
# https://stackoverflow.com/questions/26012132/zero-mq-socket-recv-call-is-blocking
# -----
from datetime import datetime
import zmq
# import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library
import time
from time import sleep     # Import the sleep function from the time module
GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
GPIO.setup(16, GPIO.OUT, initial=GPIO.LOW) 

#------- connection setting
context = zmq.Context()
#  Socket to talk to server
print("Connecting to hello world server…")
#socket = context.socket(zmq.REQ)
socket = context.socket(zmq.SUB)

socket.connect("tcp://11.11.11.11:5556") #change this to ip-server
topicfilter ="pi-depan"
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter, encoding='utf-8')
# KeepAlive whe connection unstable
socket.setsockopt(zmq.TCP_KEEPALIVE, 1)
socket.setsockopt(zmq.TCP_KEEPALIVE_IDLE, 300)
socket.setsockopt(zmq.TCP_KEEPALIVE_INTVL, 300)

#------- electrical setting
pin_out = 16

#------- state
Open_status = False
count_close = 0
old_time = time.time()

def magnet_on():
    GPIO.output(pin_out, GPIO.HIGH)
    print("on")

def magnet_off():
    GPIO.output(pin_out, GPIO.LOW)
    print("off")

def display(pesan):
    pass

def scalling(bbox):
    targetSize = (270,250)
    originalSize = (400,300)
    scaleX = targetSize[0]/originalSize[0]
    scaleY = targetSize[1]/originalSize[1]

    bbox[0] = int(bbox[0]*scaleX)
    bbox[1] = int(bbox[1]*scaleY)
    bbox[2] = int(bbox[2]*scaleX)
    bbox[3] = int(bbox[3]*scaleY)
    return bbox

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

def main():
    # no received handle, so program can running and not stuck using zmq.NOBLOCK
    global Open_status, old_time
    try:
        pred_name, pred_bbox = rcvMsg()
        print(pred_name, pred_bbox)
        
        if pred_name == "Unknown":
            #socket.send(b"High")
            print("Unknown, Not Open")
            Open_status = False
            display("Silakan Hubungi Petugas")

        elif pred_name != "unknown":
            print("Silahkan Masuk!")
            Open_status = True

    except zmq.Again as e:
        # print("-- no received")
        
        pred_bbox = None
        

    # Jika Pintu Tebuka
    if Open_status == True:
        if time.time() - old_time > 3:
            magnet_on()
            Open_status = False
            old_time = time.time()
        magnet_off()
    if pred_bbox is None:
        return None, None
    else:
        return pred_bbox, pred_name
        