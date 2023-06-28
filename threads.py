import numpy as np
import cv2
import threading
from copy import deepcopy
import time
import HandTrackingModule as htm

thread_lock = threading.Lock()
thread_exit = False


class myThread(threading.Thread):
    def __init__(self, camNo, hCam, wCam):
        super(myThread, self).__init__()
        self.camNo = camNo
        self.hCam = hCam
        self.wCam = wCam
        self.img = np.zeros((hCam, wCam, 3), dtype=np.uint8)

    def run(self):
        global thread_exit
        cap = cv2.VideoCapture(self.camNo)
        # cap.set(3, self.wCam)
        # cap.set(4, self.hCam)
        pTime = 0
        while not thread_exit:
            ret, img = cap.read()
            if self.camNo == 0:
                img = cv2.flip(img, 1)
            if ret:
                img = cv2.resize(img, (self.wCam, self.hCam))
                thread_lock.acquire()
                self.img = img
                # cTime = time.time()
                # fps = 1 / (cTime - pTime)
                # pTime = cTime
                # cv2.putText(img, str(int(fps)), (15, 40),cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

                thread_lock.release()
            else:
                thread_exit = True

        cap.release()

    def get_img(self):
        return deepcopy(self.img)


def main():
    global thread_exit
    camNo = 0
    wCam = 640
    hCam = 480
    thread = myThread(camNo, hCam, wCam)
    thread.start()

    while not thread_exit:
        thread_lock.acquire()
        img = thread.get_img()
        thread_lock.release()
      
        cv2.imshow('Video', img)
        if cv2.waitKey(1) & 0xFF == 27:
            thread_exit = True
    thread.join()


if __name__ == "__main__":
    main()
