import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time

class PushButton():
	def __init__(self, pin_tombol):
		self.pin_tombol = pin_tombol
		GPIO.setup(self.pin_tombol, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

	def isPressed(self):
		if GPIO.input(self.pin_tombol) == GPIO.LOW:
			return True
		else:
			return False

class Relay():
    def __init__(self, pin_relay, name="default"):
        self.pin_relay = pin_relay
        self.name_relay = name
        GPIO.setup(self.pin_relay, GPIO.OUT, initial=GPIO.LOW) 

    def on(self,v=False):
        GPIO.output(self.pin_relay, GPIO.LOW)
        if v:
            print(f"Relay {self.name_relay} GPIO.LOW")

    def off(self, v=False):
        GPIO.output(self.pin_relay, GPIO.HIGH)
        if v:
            print(f"Relay {self.name_relay} GPIO.HIGH")



class BeepBuzzer():
	def __init__(self, pin_buzzer):
		self.pin_buzzer = pin_buzzer
		GPIO.setup(self.pin_buzzer, GPIO.OUT, initial=GPIO.LOW)

	def on(self, duration=0.1, v=False):
		GPIO.output(self.pin_buzzer, GPIO.HIGH)
		if v:
			print("beep ON selama "+ str(waktu)+" s")
		time.sleep(duration)

	def off(self, duration=0.0, v=False):
		GPIO.output(self.pin_buzzer, GPIO.LOW)
		if v:
			print("beep OFF selama "+ str(waktu)+" s")
		time.sleep(duration)

class Jarak():
    def __init__(self, pinTrig, pinEcho):
        self.pTrig = pinTrig
        self.pEcho = pinEcho
        GPIO.setup(self.pTrig, GPIO.OUT)
        GPIO.setup(self.pEcho, GPIO.IN)

    def detect(self, m=None, b=None):
        # set Trigger to HIGH 
        GPIO.output(self.pTrig, True) 
        # set Trigger after 0.01ms to LOW 
        time.sleep(0.00001) 
        GPIO.output(self.pTrig, False)

        startTime = time.time() 
        stopTime = time.time()

        # save start time 
        while 0 == GPIO.input(self.pEcho): 
            startTime = time.time()
        # save time of arrival 
        while 1 == GPIO.input(self.pEcho): 
            stopTime = time.time()
        # time difference between start and arrival 
        TimeElapsed = stopTime - startTime 
        # multiply with the sonic speed (34300 cm/s) 
        # and divide by 2, because there and back 
        distance = (TimeElapsed * 34300) / 2
        if (m!=None and b!=None):
            # faktor regresi linear
            distance = m*distance+b

        return distance
