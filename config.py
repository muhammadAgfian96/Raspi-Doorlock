from easydict import EasyDict as edict

configs = edict()

#------- GET FROM SERVER
configs.raspi.addr_server = "tcp://11.11.11.11:5556"
configs.raspi.topicfilter = "pi-depan"

configs.raspi.p_magnet_relay = 32 # ---- relay
configs.raspi.p_led_relay    = 11 # 
configs.raspi.p_trig_jarak   = 18 # ---- sensor jarak
configs.raspi.p_echo_jarak   = 16 # 
configs.raspi.p_exit_btn     = 29 # ---- button
configs.raspi.p_buzzer       = 12 # ---- beep
configs.raspi.p_RST_RFID     = 13 # ---- RFID
configs.raspi.p_MISO_RFID    = 35 
configs.raspi.p_MOSI_RFID    = 38
configs.raspi.p_SCK_RFID     = 40
configs.raspi.p_SDA_RFID     = 36
configs.raspi.p_SDA_THERM    = 3  # ---- Thermal Cam
configs.raspi.p_SCL_THERM    = 5