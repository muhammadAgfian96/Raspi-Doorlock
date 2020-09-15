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
