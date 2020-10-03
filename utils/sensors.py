import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time
from utils.RFIDcard.MFRC522 import MFRC522

from utils.ThermCAM.SeedAMG8833 import AMG8833
import numpy as np
from scipy.interpolate import griddata
import math
from colour import Color




class PushButton():
    def __init__(self, pin_tombol):
        self.__pin_tombol = pin_tombol
        GPIO.setup(self.__pin_tombol, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
    @property
    def isPressed(self):
        """
        know condition push
        """
        if GPIO.input(self.__pin_tombol):
            print('button HIGH')
            return True
        else:
            print('button LOW')
            return False
        
class Relay():
    def __init__(self, pin_relay, name="default"):
        self.__pin_relay = pin_relay
        self.__name_relay = name
        GPIO.setup(self.__pin_relay, GPIO.OUT, initial=GPIO.LOW) 

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

        #startTime = time.time() 
        #stopTime = time.time()

        # save start time
        runTimeStart = time.time()
        while 0 == GPIO.input(self.__pEcho):
            timeStartJarak = time.time()
            if timeStartJarak - runTimeStart > 0.25:
                print('[Error Sensors] Timeout 0 Jarak!')
                return 60
        # save time of arrival 
        while 1 == GPIO.input(self.__pEcho): 
            timeStopJarak = time.time()
            if timeStopJarak - runTimeStart > 0.25:
                print('[Error Sensors] Timeout 1 Jarak!')
                return 60
        # time difference between start and arrival 
        TimeElapsed = timeStopJarak - timeStartJarak 
        # multiply with the sonic speed (34300 cm/s) 
        # and divide by 2, because there and back 
        distance = (TimeElapsed * 34300) / 2
        if (m!=None and b!=None):
            # faktor regresi linear
            distance = m*distance+b
        if v:
            print("[s_jarak] {:.2f} cm".format(distance))
        return distance

class Card(MFRC522):
    def __init__(self, dev_spi = '/dev/spidev1.2'):
        self.__MIFAREReader = MFRC522(dev = dev_spi)

    def read_card(self):
        # Scan for cards    
        (status,TagType) = self.__MIFAREReader.MFRC522_Request(self.__MIFAREReader.PICC_REQIDL)

        # If a card is found
        if status == self.__MIFAREReader.MI_OK:
            print("Card detected")
        
        # Get the UID of the card
        (status,uid) = self.__MIFAREReader.MFRC522_Anticoll()
        #print("[RFID] stats and id: ", status, uid)
        # If we have the UID, continue
        if status == self.__MIFAREReader.MI_OK:

            # Print UID
            print("[RFID] Card read UID: %s-%s-%s-%s" % (uid[0], uid[1], uid[2], uid[3]))
        
            # This is the default key for authentication
            #key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
            
            # Select the scanned tag
            #self.__MIFAREReader.MFRC522_SelectTag(uid)

            # Authenticate
            #status = self.__MIFAREReader.MFRC522_Auth(self.__MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

            # Check if authenticated
            #if status == self.__MIFAREReader.MI_OK:
            #    self.__MIFAREReader.MFRC522_Read(8)
            #    self.__MIFAREReader.MFRC522_StopCrypto1()
            #else:
            #    print("Authentication error")
            
            return "%s%s%s%s" % (uid[0], uid[1], uid[2], uid[3])
        else:
            return None

class CamTherm(AMG8833):
    def __init__(self, alamat, ukuran_pix=120j, minTemp=30, maxTemp=38):
        self._cam = AMG8833(addr=alamat)
        self._points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
        self._ukuran = ukuran_pix
        self._grid_x, self._grid_y = np.mgrid[0:7:self._ukuran, 0:7:self._ukuran]
        #low range of the sensor (this will be blue on the screen)
        self._MINTEMP = minTemp

        #high range of the sensor (this will be red on the screen)
        self._MAXTEMP = 31

        #how many color values we can have
        self._COLORDEPTH = 1024
        self._points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
        self._blue = Color("indigo")
        self._colors = list(self._blue.range_to(Color("red"), self._COLORDEPTH))

        self._colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in self._colors]



	#some utility functions
    def _constrain(self, val, min_val, max_val):
        return min(max_val, max(min_val, val))

    def _map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def _regresikan(self, pixels_list, shape=(8,8)):
        print(type(pixels_list), pixels_list)

        rata2 = np.array(list(pixels_list)).mean()
        pixels_2d = np.array(pixels_list).reshape(shape)
        
        logical_greater = pixels_2d > rata2 + 1.7
        logical_minor = pixels_2d < rata2 +0.7
        
        factor_greater = pixels_2d[logical_greater] * (-0.014523) + 1.456925
        factor_minor = pixels_2d[logical_minor] * (-0.009277) + 1.115660
        
        greater = pixels_2d[logical_greater] * factor_greater
        minor = pixels_2d[logical_minor] * factor_minor
        
        pixels_2d[logical_greater] = greater
        pixels_2d[logical_minor] = minor
        # print(rata2)        
        # print(np.array(list(pixels_list)).reshape(-1,1).shape)
        pixels_1d = pixels_2d.reshape((1, max(np.array(list(pixels_list)).reshape(-1,1).shape)))
        
        return pixels_2d, list(pixels_1d[0]), rata2

    def getThermal(self,):
        pixels_origin = self._cam.read_temp()
        #print(pixels_origin, type(pixels_origin))

        pixels_2d, pixels_origin, rata2 = self._regresikan(pixels_origin)
        # print(pixels_origin, type(pixels_origin))

        pixels = [self._map(p, self._MINTEMP, self._MAXTEMP, 0, self._COLORDEPTH - 1) for p in pixels_origin]

        #perdorm interpolation
        bicubic = griddata(self._points, pixels, (self._grid_x, self._grid_y), method='cubic')

        #--- proses kalibrasi
        suhu = np.max(pixels_origin)
        # print(suhu)

        #draw everything
        data_img = np.zeros((bicubic.shape[0],bicubic.shape[1],3), dtype=np.uint8)
        for ix, row in enumerate(bicubic):
            for jx, pixel in enumerate(row):
                r,g,b = self._colors[self._constrain(int(pixel), 0, self._COLORDEPTH- 1)]
                data_img[jx,ix] = [r,g,b]
        # pygame.display.update()
        data_img = np.rot90(data_img, k=1)
        data_img = np.flip(data_img, 1)

        return data_img, suhu
