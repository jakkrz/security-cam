from typing import Optional
import time
import datetime
import socket

import cv2
from networking import ADDRESS, send_file

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(ADDRESS)

cap = cv2.VideoCapture(0)
cap.set(cv2.CV_CAP_PROP_FPS, 60)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')

detecting = False
last_detected = None
SECONDS_TO_RECORD_AFTER_DETECTION = 5

frame_size = (int(cap.get(3)), int(cap.get(4)))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

def highlight(to_highlight, color):
    for (x, y, width, height) in to_highlight:
        cv2.rectangle(frame, (x, y), (x + width, y + height), color, 3)

current_filename = ''
out: Optional[cv2.VideoWriter] = None

try:
    while True:
        _, frame = cap.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        bodies = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) + len(bodies) > 0:
            if detecting:
                last_detected = None
            else:
                detecting = True
                current_time = datetime.datetime.now().strftime('%d-%m-%Y-%H-%M-%S')
                current_filename = f'client-files/{current_time}.mp4'

                out = cv2.VideoWriter(current_filename, fourcc, 20, frame_size)
                print('Started recording!')
        elif detecting:
            if last_detected is not None:
                if time.time() - last_detected >= SECONDS_TO_RECORD_AFTER_DETECTION:
                    detecting = False
                    last_detected = None
                    out.release()
                    print('Stopped recording!')
                    send_file(sock, current_filename)
            else:
                last_detected = time.time()

        if detecting:
            out.write(frame)

except KeyboardInterrupt:
    pass

if out is not None:
    out.release()

cap.release()
cv2.destroyAllWindows()

sock.shutdown(socket.SHUT_RDWR)
sock.close()
