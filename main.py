import os.path
import sys
import threading
import time

import numpy as np

from UI.camera import Ui_MainWindow
import cv2
from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsPixmapItem, \
    QGraphicsItem, QGraphicsScene, QMessageBox
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap
from UI.newGraphicview import GraphicsView
from SDK import sdk
from threading import Thread


class camera(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # 建立父窗口
        self.window = QMainWindow()
        # 建立原始捕获窗口及相关组件
        self.cap_win = QMainWindow(parent=self.window)
        self.cap_scene = QGraphicsScene()
        self.cap_view = GraphicsView()
        self.cap_view.setScene(self.cap_scene)
        self.cap_win.setCentralWidget(self.cap_view)
        self.cap_win.setWindowTitle("原始捕获")
        self.cap_win.setGeometry(400, 400, 800, 600)
        # 建立识别捕获窗口及相关组件
        self.rec_win = QMainWindow(parent=self.window)
        self.rec_scene = QGraphicsScene()
        self.rec_view = GraphicsView()
        self.rec_view.setScene(self.rec_scene)
        self.rec_win.setCentralWidget(self.rec_view)
        self.rec_win.setWindowTitle("识别捕获")
        self.rec_win.setGeometry(400, 400, 800, 600)
        # 初始化UI
        self.setupUi(self.window)
        self.window.setGeometry(100, 100, 300, 200)
        self.window.setWindowTitle("控制台")
        # 初始化槽函数
        self.slot_init()

    def slot_init(self):
        self.op_button.clicked.connect(
            self.camera_op
        )

    def camera_op(self):
        if self.cap_win.isHidden():
            self.op_button.setText('关闭相机')
            self.cap_win.show()
        else:
            self.op_button.setText('开启相机')
            self.cap_scene.clear()
            self.cap_win.close()

    def set_raw_view(self, img):
        show_image = cv2qimg(img)
        self.cap_scene.clear()
        cap_item = QGraphicsPixmapItem(QPixmap(show_image))
        cap_item.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.cap_scene.addItem(cap_item)
        self.cap_view.fitInView(cap_item, Qt.AspectRatioMode.KeepAspectRatio)


# SDK相关定义
SDK = sdk()

SDK.connect_cam(b"192.168.10.100", 65300)

if SDK.cam_handle < 0:
    print("未连接摄像头")
    sys.exit()

free = False
in_progress = False

img_raw = None
img_8bit = None

# 摄像头捕获线程
def cap_thread():
    global free, img_raw, img_8bit
    while True:
        if not threading.main_thread().is_alive():
            SDK.disconnect_cam()
            break
        img_raw = SDK.get_frame()
        img_8bit = SDK.process_img_data(img_raw)
        ui.set_raw_view(img_8bit)
        if not free and not in_progress:
            SDK.save_img(img_8bit, '0.png')
            free = True
        time.sleep(0.04)

def rec_thread():
    global free, in_progress, img_8bit
    while True:
        if not threading.main_thread().is_alive():
            break
        if free:
            in_progress = True
            free = False
            SDK.calculate_sfr()
            SDK.draw_result(img_8bit)
            in_progress = False

def cv2qimg(src) -> QImage:
    img = cv2.cvtColor(src, cv2.COLOR_BGR2RGB)
    qimg = QImage(img.data, img.shape[1], img.shape[0], QImage.Format.Format_RGB888)
    return qimg


# 照片识别进程
cap_t = Thread(target=cap_thread)
rec_t = Thread(target=rec_thread)

# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = camera()
    ui.window.show()
    cap_t.start()
    rec_t.start()
    sys.exit(app.exec())
