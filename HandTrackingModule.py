#!/usr/bin/python3
import cv2
import mediapipe as mp
import math
import time
import numpy as np


class handDetector:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        """
        :param mode: 是否将输入图像视为一批静态的, 甚至不相关的图像或视频流
        :param maxHands: 最大数量的检测
        :param detectionCon: 最小的信心值([0.0,1.0]), 检测被认为是成功的
        :param trackCon: 最小的信心值([0.0,1.0]), 手地标被认为成功地跟踪
        """
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands

        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]


    def findHands(self, img, draw=True):
        # 转化cv2的BGR色彩模式为mediapipe的RGB模式
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        """
        # 检测手返回创建的hands对象的属性
        # multi_hand_landmarks          ：每个手
        # multi_hand_world_landmarks    ：每个点坐标
        # multi_handedness              ：左右手
        """
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    # 绘制手的线条和关键点
                    # 使用参数更改颜色 landmark_drawing_spec=self.mpDraw.DrawingSpec(color=(255, 255, 160))
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
                    # self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS,
                    #                            landmark_drawing_spec=self.mpDraw.DrawingSpec(color=(255, 255, 160)))

        return img

    def findPosition(self, img, handNo=0, draw=True):
        xList = []
        yList = []
        bbox = []

        # 指尖id 4,8,12,16,20
        self.lmList = []

        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            # 获取每个点id和坐标信息
            for id, lm in enumerate(myHand.landmark):
                img_h, img_w, img_c = img.shape
                # 将原有的比例坐标转化为像素坐标，便于人理解
                cx, cy = int(lm.x * img_w), int(lm.y * img_h)

                xList.append(cx)
                yList.append(cy)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 10, (73, 156, 84), cv2.FILLED)

            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = xmin, ymin, xmax, ymax
            # 方框标记手指区域
            if draw:
                cv2.rectangle(img, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20),(0, 255, 0), 2)

        return self.lmList, bbox


    def fingersUp(self):
        fingers = []

        # 拇指
        if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # 其他手指
        for id in range(1, 5):
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        # totalFingers = fingers.count(1)

        return fingers


    def findDistance(self, p1, p2, img, draw=True, r=15, t=3):
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            pass
            cv2.line(img, (x1, y1), (x2, y2), (43, 45, 48), t)
            cv2.circle(img, (x1, y1), r, (43, 45, 48), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (43, 45, 48), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (43, 45, 48), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        
        
        # print(x1, y1, x2, y2, cx, cy, length)
        
        return length, img, [x1, y1, x2, y2, cx, cy]


def main():
    # fps
    pTime = 0

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    detector = handDetector()

    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)

        img = detector.findHands(img)

        lmList, bbox= detector.findPosition(img)

        print(type(lmList))
        # if len(lmList) != 0:
        #     print(lmList)


        cTime = time.time()
        fps = 1 // (cTime - pTime)
        pTime = cTime
        cv2.putText(img, "FPS: " + str(fps), (10, 50), cv2.FONT_HERSHEY_PLAIN, 3, (132, 21, 200))

        cv2.imshow("Image", img)
        # cv2.waitKey(1)
        if cv2.waitKey(1) == 27:  # wait for ESC
            cv2.destroyAllWindows()
            break


if __name__ == "__main__":
    main()
