#--- Ref---
# written by:agfian
# https://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/patterns/pubsub.html
# https://stackoverflow.com/questions/26012132/zero-mq-socket-recv-call-is-blocking
# -----
from datetime import datetime
import zmq
import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library
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
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)

#------- electrical setting
pin_out = 16

#------- state
Open_status = False
count_close = 0

def magnet_on():
    GPIO.output(pin_out, GPIO.HIGH)
    print("High")

def magnet_off():
    GPIO.output(pin_out, GPIO.LOW)
    print("Low")

def display(pesan):
    pass

def rcvMsg():
    message = socket.recv(flags=zmq.NOBLOCK)
    now = datetime.now()
    now = now.strftime("%d/%m/%Y-%H:%M:%S")
    name = str(message).split("'")[1]
    print("-- Received %s %s" % (message,now))
    name = name.split(" ")[1]
    return name


while True:
    
    # no received handle, so program can running and not stuck using zmq.NOBLOCK
    try:
        pred_name = rcvMsg().lower()
        
        if pred_name.lower() == "unknown":
            #socket.send(b"High")
            print("Unknown, Not Open")
            Open_status = False
            display("Silakan Hubungi Petugas")

        elif pred_name != "unknown":
            print("Silahkan Masuk!")
            Open_status = True

    except zmq.Again as e:
        #print("-- no received")
        pass

    # Jika Pintu Tebuka
    if Open_status == True:
        magnet_off()
        sleep(3)
        magnet_on()
        Open_status = False