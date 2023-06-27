import numpy as np
import cv2
import threading
from copy import deepcopy

thread_lock = threading.Lock()
thread_exit = False


class myThread(threading.Thread):
    def __init__(self, camera_id, img_height, img_width):
        super(myThread, self).__init__()
        self.camera_id = camera_id
        self.img_height = img_height
        self.img_width = img_width
        self.img = np.zeros((img_height, img_width, 3), dtype=np.uint8)

    def get_img(self):
        return deepcopy(self.img)

    def run(self):
        global thread_exit
        cap = cv2.VideoCapture(self.camera_id)
        while not thread_exit:
            ret, img = cap.read()
            if ret:
                img = cv2.resize(img, (self.img_width, self.img_height))
                thread_lock.acquire()
                self.img = img
                thread_lock.release()
            else:
                thread_exit = True
        cap.release()


def main():
    global thread_exit
    camera_id = 0
    img_height = 480
    img_width = 640
    thread = myThread(camera_id, img_height, img_width)
    thread.start()

    while not thread_exit:
        thread_lock.acquire()
        img = thread.get_img()
        thread_lock.release()

        cv2.imshow('Video', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            thread_exit = True
    thread.join()


if __name__ == "__main__":
    main()
