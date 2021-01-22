import logging
import os
import time
from logging.handlers import TimedRotatingFileHandler
import datetime as dt

# from easydict import EasyDict as edict
default_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', "%Y-%m-%d %H:%M:%S")


def setup_logger(name:str, log_file:str, level=logging.DEBUG, 
                 folder_name:str='logs', 
                 to_console:bool=False, removePeriodically:bool=False,
                 backupCount:int=7, when:str = 'D', interval:int = 7, 
                 formatter = default_formatter):
    """
    when:       
        'S': Seconds
        'M': Minutes
        'H': Hours
        'D': Days
    """

    full_path = folder_name+'/'+log_file

    def filer(self):
        now = dt.datetime.now()
        fullTime = ''
        if when.upper() == 'S': 
            fullTime = now.strftime("%Y-%m-%d_%H-%M-%S")
        elif when.upper() == 'M':
            fullTime = now.strftime("%Y-%m-%d_%H-%M")
        elif when.upper() == 'H':
            fullTime = now.strftime("%Y-%m-%d_%H")
        elif when.upper() == 'D':
            fullTime = now.strftime("%Y-%m-%d")
        return full_path + '.'+ fullTime

    def getPathName():
        now = dt.datetime.now()
        fullTime = ''
        if when.upper() == 'S': 
            fullTime = now.strftime("%Y-%m-%d_%H-%M-%S")
        elif when.upper() == 'M':
            fullTime = now.strftime("%Y-%m-%d_%H-%M")
        elif when.upper() == 'H':
            fullTime = now.strftime("%Y-%m-%d_%H")
        elif when.upper() == 'D':
            fullTime = now.strftime("%Y-%m-%d")

        return full_path + '.'+ fullTime


    if os.path.isfile(log_file):
        file_mode = 'a'
        # print('mode append')
    else:
        file_mode = 'w'
        # print('mode write')
    

    if not os.path.exists(folder_name):
        os.mkdir(path=folder_name)


    # setup for rotate time logging
    path_logs = getPathName()
    
    root_logger = logging.getLogger(name)
    root_logger.setLevel(level)

    if removePeriodically:
        # setup for rotate time logging
        auto_rotate = TimedRotatingFileHandler(filename= full_path,
                                               when=when,
                                               interval=interval,
                                               backupCount=backupCount)
        auto_rotate.rotation_filename = filer
        auto_rotate.setFormatter(formatter)
        root_logger.addHandler(auto_rotate)
    else:
        # setup for file logging
        # do not use if you wanna use TimedRotatingFileHandler, cause make it double jobs
        # --------------------------------
        file_handler = logging.FileHandler(full_path, mode=file_mode)        
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    if to_console:
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)
        root_logger.addHandler(streamHandler)

    return root_logger


# How to Use
# ----------------------------------------------------------------
"""

test = setup_logger('my_first', 'main.log', folder_name='main_logs',removePeriodically=True,
                    interval=1, backupCount=2, when='m', to_console=True)
while True:
    test.info('hai')
    time.sleep(10)

"""