## Redesign:
```powershell
usr/bin/designer <name>.ui
```

## Extract design ui --> py:
```powershell
pyuic5 -x <name_ui_lu>.ui -o <name_py_lu>.py
```

## Compile design qrc --> rc:
```powershell
pyrcc -x <name_ui_lu>.ui -o <name_py_lu>.py`
```


## Running stream video
1. Check: `v4l2-ctl --list-devices`
2. looking for raspi camera:
```powershell
mmal service 16.1 (platform:bcm2835-v4l2):
	/dev/video0
```
3. running this
```powershell
cvlc --no-audio \
v4l2:///dev/video0 \
--v4l2-height 300 \
--v4l2-width 400 \
--v4l2-chroma MJPG \
--sout '#standard{access=http{mime=multipart/x-mixed-replace;boundary=--7b3cc56e5f51db803f790dad720ed50a},mux=mpjpeg,dst=:8555/}' \
-I dummy
```
test

## Setting Up Camera

to see what you can control on your camera:

```powershell
v4l2-ctl -list-control

```

```powershell
v4l2-ctl -d /dev/video0 -c focus_auto=0 
v4l2-ctl -d /dev/video0 -c brightness=150
v4l2-ctl -d /dev/video0 -c contrast=0
v4l2-ctl -d /dev/video0 -c gain=150
v4l2-ctl -d /dev/video0 -c sharpness=80
v4l2-ctl -d /dev/video0 -c exposure_auto_priority=0
v4l2-ctl -d /dev/video0 -c exposure_auto=1
v4l2-ctl -d /dev/video0 -c exposure_auto_absolute=170
```