import time
import cv2
import numpy as np
import pyautogui as auto

import HandTrackingModule as htm


################# 画面属性
wCam, hCam = 640, 480
frameR = 100
#################
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)


pTime = 0
detector = htm.handDetector(maxHands=1)

wScr, hScr = auto.size()
# print(wScr, hScr)

while True:
    # 1.找到手地标
    success, img = cap.read()
    # 反转镜头左右
    img = cv2.flip(img, 1)

    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    # 2.找到食指和中指
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        # print(x1, x2, y1, y2)

        # 3.检查竖起的手指

        fingers = detector.fingersUp()
        # print(fingers)
        # 画屏幕范围框
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)
        # 4.只有食指竖起时：移动模式
        if fingers[1] == 1 and fingers[2] == 0:
            # 5.转换坐标;
            x3 = np.interp(x1, (frameR, wCam-frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam-frameR), (0, hScr))

            # 6.平滑值
            # 7.移动鼠标

            auto.moveTo(x3, y3)
            cv2.circle(img, (x1, y1), 15, (255, 0, 0), cv2.FILLED)

        # 8.食指和中指都竖起时：点击模式
        if fingers[1] ==1 and fingers[2] == 1:
            length, img, _ = detector.findDistance(8, 12, img)
            # print(length)
            # if length < 40:
            #     cv2.circle(img, ())

        # 9.找两指距离
        # 1o.距离最短时检查鼠标
        # 11.帧率
    cTime = time.time()

    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    # 12. Display
    cv2.imshow("Image", img)
    if cv2.waitKey(1) == 27:
        break
