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


context = zmq.Context()
#  Socket to talk to server
print("Connecting to hello world server…")
#socket = context.socket(zmq.REQ)
socket = context.socket(zmq.SUB)

socket.connect("tcp://192.168.0.5:5556") #change this to ip-server
topicfilter ="1"
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
Open_status = False
count_close = 0
while True:
    
    if Open_status == True:
        GPIO.output(16, GPIO.HIGH)
        print("High")
        count_close+=1
        sleep(2)        
        GPIO.output(16, GPIO.LOW) 
        Open_status=False
        count_close=0
        print("Low")
    
    try:
        message = socket.recv(flags=zmq.NOBLOCK)
        now = datetime.now()
        now = now.strftime("%d/%m/%Y-%H:%M:%S")
        name = str(message).split("'")[1]
        print("-- Received %s %s" % (message,now))
        name = name.split(" ")[1]
        if name == "boy":
            #socket.send(b"High")
            print("open")
            Open_status = True
              
    except zmq.Again as e:
        #print("-- no received")
        pass