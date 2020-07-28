# Raspi-Doorlock
using face verification to lock or unlock the door.


cvlc --no-audio \
v4l2:///dev/video0 \
--v4l2-height 300 \
--v4l2-width 400 \
--v4l2-chroma MJPG \
--sout '#standard{access=http{mime=multipart/x-mixed-replace;boundary=--7b3cc56e5f51db803f790dad720ed50a},mux=mpjpeg,dst=:8555/}' \
-I dummy

sudo modprobe bcm2835-v4l2
```
mmal service 16.1 (platform:bcm2835-v4l2):
	/dev/video0
```

```markdown
cvlc --no-audio \
v4l2:///dev/video0 \
--v4l2-height 300 \
--v4l2-width 400 \
--v4l2-chroma MJPG \
--sout '#transcode{acodec=mpga,ab=128,channels=2,samplerate=44100,threads=4,audio-sync=1}:standard{access=http{mime=multipart/x-mixed-replace;boundary=--7b3cc56e5f51db803f790dad720ed50a},mux=mpjpeg,dst=:8555/}' \
-I dummy
```