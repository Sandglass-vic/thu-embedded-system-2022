#!/usr/bin/sh
/usr/bin/mjpg_streamer -i "/usr/lib/mjpg-streamer/input_uvc.so -r 640x360
-d /dev/video0 -f 30" -o "/usr/lib/mjpg-streamer/output_http.so -p 8080 -w /
usr/share/mjpg-streamer/www"