import cv2
  
vid = cv2.VideoCapture(0)
while(True):
    ret, frame = vid.read()
    if ret:
        cv2.imwrite('test.jpg', frame)
        break
    else:
        cv2.waitKey(1)
vid.release()