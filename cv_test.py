import cv2
import cv2.cv
import time

ramp_frames = 30
camera_port = 0
camera = cv2.VideoCapture(camera_port)
cv2.namedWindow("w1", cv2.CV_WINDOW_AUTOSIZE)

def get_image():
    retval, im = camera.read()
    return im

for i in xrange(ramp_frames):
    temp = get_image()
    
time.sleep(.1)
frame = get_image();
cv2.imshow("w1", frame)
cv2.imwrite("test_image_3.png", frame)
time.sleep(2)

del(camera)
