import cv2
import time

from pi_video_stream import PiVideoStream

vs = PiVideoStream()
vs.start()
time.sleep(2.0)

while True:
    frame = vs.read()
    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.imshow('frame', gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vs.stop()

