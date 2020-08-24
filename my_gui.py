from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import robot_info
from robot_info import *
import datetime
import numpy as np

width, height = 640, 480
camera1= 'http://11.11.11.12:8555'
camera=0
# camera2 = 'rtsp://admin:adminsdi123@103.133.223.50:554/Streaming/channels/101'
camera2 = 'http://11.11.11.22:8555'
cap = cv2.VideoCapture(camera1)

root = Tk()
root['bg'] = 'blue'
content = ttk.Frame(root, padding=(2,2,2,2))
VideoContent = ttk.Frame(content, borderwidth=3,  width=300, height=200)
ImageContent = ttk.Frame(content, borderwidth=3,  width=300, height=200)

ls_info = ttk.Label(content, 
                    text="Terakhir Masuk:", 
                    font=('Helvetica', 14, 'bold'), 
                    background='#0EBC63', 
                    foreground='white')

ls_history_border = ttk.Frame(content, 
                              relief="sunken",
                              style='ls_hist_border.TFrame')

ls_history = Listbox(ls_history_border, 
                     height=7, 
                     borderwidth=0, 
                     highlightthickness=0, 
                     background='#B9E8BB')

ls_history.grid(column=0, row=0, 
                sticky=(N,W,E,S), 
                padx=8,pady=3)

ok = ttk.Button(content, text="Call")
cancel = ttk.Button(content, text="Quit", command=root.destroy)

waktu = ttk.Label(content, text="Date:", 
                  font=('Helvetica', 14, 'bold'))

realtime = ttk.Label(content, 
                    text=str(datetime.datetime.now().strftime("%d-%m-%Y || %H:%M:%S")), 
                    font=('Helvetica', 14, 'bold'))

content.grid(column=0, row=0, sticky=(N, S, E, W))
ls_info.grid(column=3, row=0, columnspan=2, sticky=(N, W), padx=5)
ls_history_border.grid(column=3, row=1, columnspan=2, sticky=(N, E, W), padx=5)
waktu.grid(column=0, row=3, sticky=(N, E))
realtime.grid(column=1, row=3, sticky=(N, E, W))
ok.grid(column=3, row=4)
cancel.grid(column=4, row=4)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

VideoContent.columnconfigure(0, weight=0)
VideoContent.grid(column=0, row=0, columnspan=3, rowspan=2, sticky=(N, S, E, W))
VideoContent.rowconfigure(0, weight=0)

ImageContent.columnconfigure(0, weight=0)
ImageContent.grid(column=3, row=2, columnspan=3, rowspan=2, sticky=(N, S, E, W))
ImageContent.rowconfigure(0, weight=0)

video = ttk.Label(VideoContent)
video.grid(column=0,row=0, columnspan=3)

muka_satu = ttk.Label(ImageContent)
muka_satu.grid(column=3,row=0, columnspan=2)

styleContent = ttk.Style(content)
styleContent.configure('TLabel', background='white', foreground='black')
styleContent.configure('TFrame', background='white', )
styleContent.configure('ls_hist_border.TFrame', background='#B9E8BB')

content.columnconfigure(0, weight=3)
content.columnconfigure(1, weight=3)
content.columnconfigure(2, weight=3)
content.columnconfigure(3, weight=1)
content.columnconfigure(4, weight=1)

content.rowconfigure(1, weight=1)

s = ttk.Scrollbar(ls_history_border, orient=VERTICAL, command=ls_history.yview)
s.grid(column=1, row=0, sticky=(N, S, E),padx=1)
ls_history['yscrollcommand'] = s.set


def show_time():
    realtime.config(text=str(datetime.datetime.now().strftime("%d-%m-%Y | %H:%M:%S")))
    realtime.after(1000, show_time)

def insert_list(nama):
    name_time = "%s \t %s" % (nama, str(datetime.datetime.now().strftime("%H:%M"))) #:%S
    ls_history.insert(0, name_time)
    # ls_history.after(1000, insert_list)

def fullscreen(root):
    width, height = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (width, height))


def show_frame():
    global cap
    ada, frame = cap.read()
    try:
        if ada:
            frame = cv2.resize(frame, (270,250))
            frame_flip = cv2.flip(frame, 1)
            cv2image = cv2.cvtColor(frame_flip, cv2.COLOR_BGR2RGBA)
            # we process the dot

            robot_info.Open_status
            bbox, pred_name = robot_info.main()
            if bbox is not None:
                muka = frame[bbox[1]-10:bbox[3]+10, bbox[0]-20:bbox[2]+20]
                insert_list(pred_name)
                # muka = cv2.imread('muka.jpg')
                muka = cv2.resize(muka, (50,50))

                b,g,r = cv2.split(muka)
                muka = cv2.merge((r,g,b))

                muka = Image.fromarray(muka)
                mukatk = ImageTk.PhotoImage(image=muka)
                muka_satu.imgtk = mukatk
                muka_satu.configure(image=mukatk)



        else:
            cv2image = np.zeros(shape=(270,250,4))


        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        video.imgtk = imgtk
        video.configure(image=imgtk)


    except:
        print("Cant catch up image or lost connection")
        cap = cv2.VideoCapture(camera1)
        time.sleep(1.5) # warming up

    video.after(10, show_frame)



width, height = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (width, height))

# insert_list()
show_time()
show_frame()



root.config(background="#FFFFFF")
root.title("AITI ABSEN")

# UNCOMMENT THIS FOR RASPI
# fullscreen(root)
# root.bind("<Configure>", lambda b: fullscreen(root))

# root.attributes('-type', 'splash') # remove header
# root.focus_force() #biar ketengah
root.geometry("{}x{}".format(450,290)) #ukuran raspi

root.mainloop()