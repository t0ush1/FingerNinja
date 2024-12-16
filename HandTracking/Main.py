from screeninfo import get_monitors
from pynput.mouse import Controller, Button
import cv2
import numpy as np
import time
import HandTrackingModule as htm

##############################
wCam, hCam = 1280, 720  # 摄像头分辨率
frameR = 100  # 手部检测区域边界
smoothening = 5  # 平滑参数
##############################
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

# 初始化手势检测器
detector = htm.handDetector()

# 获取屏幕分辨率
monitor = get_monitors()[0]  # 获取主屏幕信息
screenWidth, screenHeight = monitor.width, monitor.height
mouse = Controller()

while True:
    success, img = cap.read()
    # 1. 检测手部，得到手指关键点坐标
    img = detector.findHands(img)
    cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (0, 255, 0), 2, cv2.FONT_HERSHEY_PLAIN)
    lmList = detector.findPosition(img, draw=False)

    # 2. 判断食指和中指是否伸出
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]  # 食指指尖坐标
        x2, y2 = lmList[12][1:]  # 中指指尖坐标
        fingers = detector.fingersUp()

        # 3. 若只有食指伸出，则进入移动模式
        if fingers[1] and not fingers[2]:
            # 坐标转换：将食指在窗口坐标转换为鼠标在桌面的坐标
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, screenWidth))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, screenHeight))

            # 平滑鼠标移动
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            # 使用 pynput 模拟鼠标移动
            mouse.position = (clocX, clocY)

            # 更新历史位置
            plocX, plocY = clocX, clocY

        # 4. 若食指和中指都伸出，则检测指头距离，距离够短则对应鼠标点击
        if fingers[1] and fingers[2]:
            length, img, pointInfo = detector.findDistance(8, 12, img)
            if length < 40:  # 距离阈值
                mouse.click(Button.left)  # 模拟鼠标左键单击
                cv2.circle(img, (pointInfo[4], pointInfo[5]), 15, (0, 255, 0), cv2.FILLED)

    # 显示FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (15, 25), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
    cv2.imshow("Image", img)
    cv2.waitKey(1)
