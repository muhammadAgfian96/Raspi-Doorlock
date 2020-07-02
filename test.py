#--- Ref---
# written by:agfian
# https://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/patterns/pubsub.html
# https://stackoverflow.com/questions/26012132/zero-mq-socket-recv-call-is-blocking
# -----

import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library
from time import sleep     # Import the sleep function from the time module
GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW) 



count_close = 0
while True:
    
    GPIO.output(8, GPIO.HIGH)
    print("High")
    count_close+=1
    sleep(5)        
    GPIO.output(8, GPIO.LOW) 
    Open_status=False
    count_close=0
    print("Low")
    sleep(5)        

    
