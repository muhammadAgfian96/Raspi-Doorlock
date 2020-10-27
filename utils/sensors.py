import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time
from utils.RFIDcard.MFRC522 import MFRC522

from utils.ThermCAM.SeedAMG8833 import AMG8833
import numpy as np
from scipy.interpolate import griddata
import math
from colour import Color
from numpy import unravel_index
import cv2
import copy
from config import *



sensor_log = setup_logger(name = 'sensor', log_file = 'sensor_logs', 
                        folder_name='sensor_logs', level = logging.DEBUG,
                        removePeriodically=True, to_console=True,
                        interval=2, backupCount=5, when='h')
calibration_log = setup_logger(name = 'calibration', log_file = 'calibration_data', 
                        folder_name='sensor_logs', level = logging.DEBUG,
                        removePeriodically=True, to_console=True,
                        interval=30, backupCount=5, when='m')

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
            sensor_log.info('[button HIGH] Pressed!')
            return True
        else:
            # sensor_log.info('[button LOW] Unpressed!')
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

    def detect(self, m=None, b=None, v=True) -> float:
        # set Trigger to HIGH 
        GPIO.output(self.__pTrig, True) 
        # set Trigger after 0.01ms to LOW 
        time.sleep(0.00001) 
        GPIO.output(self.__pTrig, False)

        timeStartJarak = time.time()
        timeStopJarak = time.time()

        # save start time
        runTimeStart = time.time()
        while 0 == GPIO.input(self.__pEcho):
            timeStartJarak = time.time()
            if timeStartJarak - runTimeStart > 0.15:
                sensor_log.warning(f'[Sensor Jarak] Time out! timeStartJarak: {timeStartJarak} seconds')
                return 60.0
        # save time of arrival 
        while 1 == GPIO.input(self.__pEcho): 
            timeStopJarak = time.time()
            if timeStopJarak - runTimeStart > 0.15:
                sensor_log.warning(f'[Sensor Jarak] Time out! timeStopJarak: {timeStopJarak} seconds')
                return 60.0
        # time difference between start and arrival 
        TimeElapsed = timeStopJarak - timeStartJarak 
        # multiply with the sonic speed (34300 cm/s) 
        # and divide by 2, because there and back 
        distance = (TimeElapsed * 34300) / 2
        if (m!=None and b!=None):
            # faktor regresi linear
            distance = m*distance+b
        if v and distance < 7:
            sensor_log.info("[Sensor Jarak] {:.2f} cm".format(distance))
        return distance

class Card(MFRC522):
    def __init__(self, dev_spi = '/dev/spidev1.2'):
        self.__MIFAREReader = MFRC522(dev = dev_spi)

    def read_card(self):
        # Scan for cards    
        (status,TagType) = self.__MIFAREReader.MFRC522_Request(self.__MIFAREReader.PICC_REQIDL)

        # If a card is found
        if status == self.__MIFAREReader.MI_OK:
            # print("Card detected")
            sensor_log.info("[RFID] Card detected")
        
        # Get the UID of the card
        (status,uid) = self.__MIFAREReader.MFRC522_Anticoll()
        #print("[RFID] stats and id: ", status, uid)
        # If we have the UID, continue
        if status == self.__MIFAREReader.MI_OK:

            # Print UID
            # print("[RFID] Card read UID: %s-%s-%s-%s" % (uid[0], uid[1], uid[2], uid[3]))
            sensor_log.info("[RFID] Card read UID: %s-%s-%s-%s" % (uid[0], uid[1], uid[2], uid[3]))
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
    def __init__(self, alamat, ukuran_pix=120j, minTemp=25, maxTemp=35):
        self._cam = AMG8833(addr=alamat)

        self._points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
        self._ukuran = ukuran_pix
        self._grid_x, self._grid_y = np.mgrid[0:7:self._ukuran, 0:7:self._ukuran]

        #low range of the sensor (this will be blue on the screen)
        self._MINTEMP = minTemp

        #high range of the sensor (this will be red on the screen)
        self._MAXTEMP = maxTemp

        #how many color values we can have
        self._COLORDEPTH = 1024
        self._points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
        self._start_color = Color("indigo")
        self._colors = list(self._start_color.range_to(Color("red"), self._COLORDEPTH))
        self._colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in self._colors]



	#some utility functions
    def _constrain(self, val, min_val, max_val):
        return min(max_val, max(min_val, val))

    def _map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def _regresikan_part_1(self, pixels_list):

        sensor_log.debug(f"[Cam Thermal] \ntype: {type(pixels_list)} \nisi: {pixels_list}")
        arr_input = np.array(pixels_list[:])
        
        arr1_mean = arr_input.mean()
        arr1_min = arr_input.min()
        arr1_max = arr_input.max()
        sensor_log.debug(f"** [Cam Thermal] {arr_input.shape} -> mean: {arr1_mean} | min: {arr1_min} | max: {arr1_max}")
        
        arr_input *= (arr_input/arr1_mean)

        return list(arr_input), arr1_mean
    
    def _regresikan_part_2(self, arr_input, arr_mean):
        """
        arr_input is 1,64 list for bicubicData
        """

        # has 2d dimentions
        expanded_arr = griddata(self._points, arr_input[:], (self._grid_x, self._grid_y), method='cubic')    
        expanded_arr *= (expanded_arr/arr_mean)
        expanded_arr_mean = expanded_arr.mean()
        expanded_arr_max = expanded_arr.max()
        expanded_arr_min = expanded_arr.min()
        sensor_log.debug(f"** [Cam Thermal] {expanded_arr.shape} -> mean: {expanded_arr_mean} | min: {expanded_arr_min} | max: {expanded_arr_max}")

        # pisahkan 2 bagian --> great than avg and lower than avg
        idx_greater = expanded_arr >= expanded_arr_mean
        idx_minor = expanded_arr < expanded_arr_mean
        
        factor_greater = expanded_arr[idx_greater] * (-0.014523) + 1.467925
        factor_minor = expanded_arr[idx_minor] * (-0.009277) + 1.215660

        new_exp_arr_greater = expanded_arr[idx_greater] * factor_greater
        new_exp_arr_minor = expanded_arr[idx_minor] * factor_minor
        
        expanded_arr[idx_greater] = new_exp_arr_greater
        expanded_arr[idx_minor] = new_exp_arr_minor

        return expanded_arr

    def _thermalToImageAndData(self, pixelsThermal):
        """
        This is for for resize the data thermal
        
        Arguments:
            - pixelsThermal (list) : list data from amgg8833 len data is 64,

        Return:
            - image_thermal = image thermal in 0 - 255
            - data_thermal  = data thermal in celcius
        """
        regression_pixel, pixels_mean = self._regresikan_part_1(pixelsThermal[:])
        bicubicData = self._regresikan_part_2(regression_pixel, pixels_mean)

        # bicubicDataNew = bicubicData[:]
        # bicubicDataNew = bicubicDataNew.reshape((1,))
        # bicubicData = griddata(self._points, pixelsThermal, (self._grid_x, self._grid_y), method='cubic')    
        


        new_pixelsThermal = [self._map(p, self._MINTEMP, self._MAXTEMP, 0, self._COLORDEPTH - 1) for p in regression_pixel]
        # bicubicImage = self._regresikan_part_2(new_pixelsThermal, np.mean(new_pixelsThermal))
        bicubicImage = griddata(self._points, new_pixelsThermal, (self._grid_x, self._grid_y), method='cubic')

        data_img = np.zeros((bicubicImage.shape[0],bicubicImage.shape[1],3), dtype=np.uint8)
        
        # mapping celcius into colors
        for ix, row in enumerate(bicubicImage):
            for jx, pixels_Thermal in enumerate(row):
                r,g,b = self._colors[self._constrain(int(pixels_Thermal), 0, self._COLORDEPTH- 1)]
                data_img[jx,ix] = [r,g,b]

        # menyamakan posisi index dengan opencv
        data_img = np.rot90(data_img, k=1)
        image_thermal = np.flip(m=data_img, axis=1)
        
        bicubicData  = np.flip(m=bicubicData, axis=0)
        data_thermal = np.flip(m=bicubicData, axis=1)

        return image_thermal, data_thermal




    def _scalling(self, orginImage, originBBOX, targetSize):
        """
        Arguments:
            - originImage   : (np.array 3d) image from webcam
            - originBBOX    : (list)        original bbox from face detection
            - targetSize    : (complex)     self._ukuran on grid data

        Return:
            - bboxScalled   : (list) bbox yang telah di scalling
            - originBBOX    : (list) original bbox
        """
        targetSize = targetSize.imag
        originalSize = orginImage.shape
        scaleX = targetSize / originalSize[1]
        scaleY = targetSize / originalSize[0]

        bboxScalled = copy.deepcopy(originBBOX)

        bboxScalled[0] = int(np.round(bboxScalled[0]) * scaleX)
        bboxScalled[1] = int(np.round(bboxScalled[1]) * scaleY)
        bboxScalled[2] = int(np.round(bboxScalled[2]) * scaleX)
        bboxScalled[3] = int(np.round(bboxScalled[3]) * scaleY)

        return bboxScalled, originBBOX

    def _inverted_scalling(self, target, origin, titikX, titikY, bbox):
        """
        Arguments:
            - target        : (np.array)        original image from webcam
            - origin        : (bil. kompleks)   ukuran_grid camera thermal 
            - bbox          : (list)            bbox yang telah di scalling 
            - titiX, titikY : (scalar)          yang telah di scalling, dan titik yang berada pada ROI bbox, bkan keselurahan imageThermal

        Return:
            - newTitik_X : (Scalar) koordinat yang telah disamakan untuk ukuran image webcam
            - newTitik_Y : (Scalar) koordinat yang telah disamakan untuk ukuran image webcam
        """

        scaleX = target.shape[1]/origin.imag
        scaleY = target.shape[0]/origin.imag
        
        newTitik_X = copy.deepcopy(titikX)
        newTitik_Y = copy.deepcopy(titikY)

        newTitik_X += bbox[0]
        newTitik_Y += bbox[1]
        
        newTitik_X = int((newTitik_X+0.5) * scaleX)
        newTitik_Y = int((newTitik_Y+0.5) * scaleY)

        return newTitik_X, newTitik_Y 


    def _cropImageData(self, imageData, xy, x2y2):
        """
        Arguments:
            xy = [x1, y1]
            x2y2 = [x2, y2]
        """
        return imageData[xy[1]:x2y2[1], xy[0]:x2y2[0]]

    def _getMaxCoordinate(self, cropThermal):
        """
        Arguments:
            - cropThermal : (np.array - celcius) one crop bbox Data-Thermal in 2d array
        """
        maxValue = np.max(cropThermal)
        (y,x) = unravel_index(cropThermal.argmax(), cropThermal.shape)
        return maxValue, (x, y)



    def getThermal(self, image, object_bboxes, youDebugging=False):
        """
        Arguments:
            - image         : (openCV image)
            - object_bboxes : (list 2d) bboxes of face
        Return:
            - data_image    : numpy array 2d data image
            - bicubicData   : numpy array 2D data thermal
            - dictSuhu      : > key     --> sum of bbox
                              > values  --> maximum value
        """
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        dictSuhu = {}
        bboxes = list(object_bboxes.values())
        ids = list(object_bboxes.keys())

        pixels_origin_first = self._cam.read_temp()

        # pixels_2d, pixels_origin, rata2 = self._regresikan(copy.deepcopy(pixels_origin_first))
        # pixel_origin = self._calibration(pixels_origin_first)
        imageThermal, dataThermal = self._thermalToImageAndData(pixels_origin_first)
        # imageThermal = cv2.cvtColor(np.array(imageThermal), cv2.COLOR_RGB2BGR)

        for bbox, idx in zip(bboxes, ids):
            bbox[0] = [bbox[0] if bbox[0] >= 0 else 0][0]
            bbox[1] = [bbox[1] if bbox[1] >= 0 else 0][0]
            bbox[2] = [bbox[2] if bbox[2] >= 0 else 0][0]
            bbox[3] = [bbox[3] if bbox[3] >= 0 else 0][0]

            ukuran_x = bbox[2]-bbox[0]

            depth = round(367 + (-7.25 * ukuran_x) + 0.0571*(ukuran_x**2) + (-0.00016*(ukuran_x**3)), 2)
            
            print('bbox sblm scalling', bbox)
            # Scalling the origin bbox so we can go with crop thermalImage
            bboxScalled, bbox = self._scalling(image, bbox, self._ukuran)
            print('bbox setelah scalling', bboxScalled)
            
            # Crop Data-Thermal (isi: celcius)
            singleCropDataThermal = self._cropImageData(imageData = dataThermal, 
                                                        xy   = (bboxScalled[0],bboxScalled[1]), 
                                                        x2y2 = (bboxScalled[2],bboxScalled[3]),
                                                        )
            
            # Crop Image-Thermal (isi: 0-255, 3 dimensi)
            singleCropImageThermal = self._cropImageData(imageData = imageThermal, 
                                                         xy   =  (bboxScalled[0],bboxScalled[1]), 
                                                         x2y2 =  (bboxScalled[2],bboxScalled[3]),
                                                         )
            
            # get maxSuhu and coordinate
            maxSuhu, (coor_x, coor_y) = self._getMaxCoordinate(singleCropDataThermal)
            new_coor_x, new_coor_y = self._inverted_scalling(target = image, 
                                                             origin = self._ukuran, 
                                                             titikX = coor_x, 
                                                             titikY = coor_y, 
                                                             bbox = bboxScalled,
                                                             )
            calibration_log.info(f"[suhu | jarak], {maxSuhu}, {depth}")
            # insert to data
            dictSuhu[idx] = {'coordinate': (new_coor_x, new_coor_y), 
                             'max' : maxSuhu,}
            
            
            # ------------------------------- Keperluan Debugging Aja! ------------------------------
            # gambar titiknya suhu tertinggi pada mukanya!
            if youDebugging:
                image = cv2.circle(img = image, 
                                center = dictSuhu[idx]['coordinate'], 
                                radius = 4, 
                                color= (0,0,255), 
                                thickness = -1,
                                )
                
                imageThermal = cv2.circle(img = np.array(imageThermal), 
                                center = (coor_x+bboxScalled[0], coor_y+bboxScalled[1]), 
                                radius = 3, 
                                color= (255,255,255), 
                                thickness = -1,
                                )
                                
                imageThermal = cv2.rectangle(imageThermal, (bboxScalled[0],bboxScalled[1]), (bboxScalled[2],bboxScalled[3]), (255,255,255), 2 )
                
                # Crop a Face
                singleCropFace = self._cropImageData(imageData = image,
                                                    xy   =  (bbox[0], bbox[1]), 
                                                    x2y2 =  (bbox[2], bbox[3]),
                                                    )

                singleCropFace = cv2.cvtColor(src = singleCropFace, code = cv2.COLOR_BGR2RGB)

                
                cv2.imshow('a FACE_', image)
                cv2.imshow('a Thermal_', imageThermal)

            # ------------------------------- Keperluan Debugging Aja! ------------------------------
            
        pixels_origin_first = np.array(pixels_origin_first).reshape((8,8))
        pixels_origin_first = np.array(pixels_origin_first).reshape((8,8))
        pixels_origin_first = np.rot90(pixels_origin_first, k=1)
        #pixels_origin_first  = np.flip(m=pixels_origin_first, axis=0) # flip horizontal
        pixels_origin_first  = np.flip(m=pixels_origin_first, axis=1) # flip vertical

        # print('\n==== dict suhu >>', imageThermal.shape, dataThermal.shape, dictSuhu)
        # sensor_log.info(f'[Cam Thermal] dict suhu {imageThermal.shape}, {dataThermal.shape}, {dictSuhu}')
        return imageThermal, dataThermal, dictSuhu, pixels_origin_first
