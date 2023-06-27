import time
import cv2
import numpy as np
import autopy

import HandTrackingModule as htm


################
# 画面属性
wCam, hCam = 1280, 760
# 参照矩形距离画面边缘距离
frameR = 250
# 平滑度 度大，动画慢
smoothening = 5
#################
pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0


cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(maxHands=1, detectionCon=0.7, trackCon=0.7)

wScr, hScr = autopy.screen.size()
# print(wScr, hScr)

while True:
    # 1.找到手地标
    success, img = cap.read()
    # # 反转镜头左右
    img = cv2.flip(img, 1)

    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    # 2.找到食指和中指
    if len(lmList) != 0:
        # 检测手指点关键点标号
        mpeFingerNo1 = 8
        mpeFingerNo2 = 4

        # mpeFingerNo1 = 8

        finger_x1, finger_y1 = lmList[mpeFingerNo1][1:]
        finger_x2, finger_y2 = lmList[mpeFingerNo2][1:]
        # print(finger_x1, finger_x2, finger_y1, finger_y2)

        # 3.检查竖起的手指
        fingers = detector.fingersUp()
        # print(fingers)

        # 画屏幕范围框 左上角和右下角确定大小
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR,hCam - frameR), (255, 0, 255), 2)

         # 9.找mpeFingerNo1, mpeFingerNo2两点距离
        length, img, lineInfo = detector.findDistance(
            mpeFingerNo1, mpeFingerNo2, img)
        print(length)

        # 4.食指竖起时：移动模式
        if fingers[1] == 1 or True :
            # 5.转换坐标 将屏幕映射到框中
            tansl_X = np.interp(finger_x1, (frameR, wCam-frameR), (0, wScr))
            tansl_Y = np.interp(finger_y1, (frameR, hCam-frameR), (0, hScr))

            # 6.平滑值 smoothening越大移动动画越慢
            clocX = plocX + (tansl_X - plocX) / smoothening
            clocY = plocY + (tansl_Y - plocY) / smoothening
            # 7.移动鼠标

            # autopy.mouse.move(clocX, clocY)
            try:
                autopy.mouse.move(clocX, clocY)
            except ValueError:
                pass

            # auto.moveTo( tansl_X, tansl_Y)

            cv2.circle(img, (finger_x1, finger_y1),13, (255, 0, 0), cv2.FILLED)
            plocX, plocY = clocX, clocY

        # 8.食指竖起，大拇指竖时：点击模式
        if fingers[4] == 1:
            # # 9.找mpeFingerNo1, mpeFingerNo2两点距离
            # length, img, lineInfo = detector.findDistance(
            #     mpeFingerNo1, mpeFingerNo2, img)
            # print(length)
        # 1o.距离最短时检查鼠标
            if length < 30:
                time.sleep(0.05)
                if length <30:
                    cv2.circle(img, (lineInfo[4], lineInfo[5]),15, (0, 255, 0), cv2.FILLED)
                    try:
                        autopy.mouse.click()
                    except TypeError:
                        pass
                    # auto.dragTo(clocX, clocY, button='left')

        # 11.帧率
    cTime = time.time()

    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50),
                cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    # 12. 显示画面
    cv2.imshow("Image", img)
    if cv2.waitKey(1) == 27:
        cap.release()
        break
        exit()
    
