import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time

class PushButton():
    def __init__(self, pin_tombol):
        self.__pin_tombol = pin_tombol
        GPIO.setup(self.__pin_tombol, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    @property
    def isPressed(self):
        """
        know condition push button
        """
        if GPIO.input(self.__pin_tombol) == GPIO.LOW:
            return True
        else:
            return False

class Relay():
    def __init__(self, pin_relay, name="default"):
        self.__pin_relay = pin_relay
        self.__name_relay = name
        GPIO.setup(self.pin_relay, GPIO.OUT, initial=GPIO.LOW) 

    def on(self,v=False):
        GPIO.output(self.__pin_relay, GPIO.LOW)
        if v:
            print(f"Relay {self.__name_relay} GPIO.LOW")

    def off(self, v=False):
        GPIO.output(self.__pin_relay, GPIO.HIGH)
        if v:
            print(f"Relay {self.__name_relay} GPIO.HIGH")



class BeepBuzzer():
    def __init__(self, pin_buzzer):
        self.__pin_buzzer = pin_buzzer
        GPIO.setup(self.__pin_buzzer, GPIO.OUT, initial=GPIO.LOW)

    def on(self, duration=0.1, v=False):
        GPIO.output(self.__pin_buzzer, GPIO.HIGH)
        if v:
            print("beep ON selama "+ str(waktu)+" s")
        time.sleep(duration)

    def off(self, duration=0.0, v=False):
        GPIO.output(self.__pin_buzzer, GPIO.LOW)
        if v:
            print("beep OFF selama "+ str(waktu)+" s")
        time.sleep(duration)

class Jarak():
    def __init__(self, pinTrig, pinEcho):
        self.__pTrig = pinTrig
        self.__pEcho = pinEcho
        GPIO.setup(self.__pTrig, GPIO.OUT)
        GPIO.setup(self.__pEcho, GPIO.IN)

    def detect(self, m=None, b=None, v=True):
        # set Trigger to HIGH 
        GPIO.output(self.__pTrig, True) 
        # set Trigger after 0.01ms to LOW 
        time.sleep(0.00001) 
        GPIO.output(self.__pTrig, False)

        startTime = time.time() 
        stopTime = time.time()

        # save start time 
        while 0 == GPIO.input(self.__pEcho): 
            startTime = time.time()
        # save time of arrival 
        while 1 == GPIO.input(self.__pEcho): 
            stopTime = time.time()
        # time difference between start and arrival 
        TimeElapsed = stopTime - startTime 
        # multiply with the sonic speed (34300 cm/s) 
        # and divide by 2, because there and back 
        distance = (TimeElapsed * 34300) / 2
        if (m!=None and b!=None):
            # faktor regresi linear
            distance = m*distance+b
        if v:
            print("[s_jarak]", distance, " cm")
        return distance

