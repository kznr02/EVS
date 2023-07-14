import os.path
import sys
import time

from UI.camera import Ui_MainWindow
import cv2
from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsPixmapItem,  \
    QGraphicsItem, QGraphicsScene, QMessageBox
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap
from UI.newGraphicview import GraphicsView
from SDK import sdk

class camera(Ui_MainWindow, sdk):
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
        # 建立QT定时器
        self.timer_camera = QTimer()
        # 建立视频捕获流
        self.image_raw = None
        self.image_8bit = None
        # 初始化UI
        self.setupUi(self.window)
        self.window.setGeometry(100, 100, 300, 200)
        self.window.setWindowTitle("控制台")
        # 初始化槽函数
        self.slot_init()

        # SDK连接相机
        self.connect_cam(b"192.168.10.100", 65300)

        if not os.path.exists('result'):
            os.mkdir('result')

    def slot_init(self):
        self.op_button.clicked.connect(
            self.camera_op
        )
        self.timer_camera.timeout.connect(
            self.show_picture
        )
        self.cap_button.clicked.connect(
            self.rec_picture
        )
        self.save_button.clicked.connect(
            self.save_result
        )
    def camera_op(self):
        if self.cam_handle < 0:
            QMessageBox.critical(self.window, '错误', '相机连接失败，请检查相机', QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
        else:
            if not self.timer_camera.isActive():
                self.timer_camera.start(40)
                self.op_button.setText('关闭相机')
                self.cap_win.show()
            else:
                self.op_button.setText('开启相机')
                self.timer_camera.stop()
                self.cap_scene.clear()
                self.cap_win.close()

    def show_picture(self):
        # 判断原始捕获窗口是否关闭
        if self.cap_win.isHidden():
            self.camera_op()
            pass
        else:
            # 捕获视频流一帧并放入显示窗口中
            # print("# 开始从远程摄像头中捕获图像 #")
            self.image_raw = self.get_frame()
            self.image_8bit = self.process_img_data(self.image_raw)
            show_image = self.cv2qimg(self.image_8bit)
            self.cap_scene.clear()
            cap_item = QGraphicsPixmapItem(QPixmap(show_image))
            cap_item.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
            self.cap_scene.addItem(cap_item)
            self.cap_view.fitInView(cap_item, Qt.AspectRatioMode.KeepAspectRatio)
            # 判断识别窗口是否存活，存活则执行每一帧的识别操作
            if not self.rec_win.isHidden():
                self.process()

    def rec_picture(self):
        if self.cap_win.isHidden():
            QMessageBox.critical(self.window, '错误', '使用识别捕获前请先开启原始捕获', QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
        else:
            # 创建识别捕获窗口
            self.rec_win.show()

    def cv2qimg(self, src) -> QImage:
        img = cv2.cvtColor(src, cv2.COLOR_BGR2RGB)
        qimg = QImage(img.data, img.shape[1], img.shape[0], QImage.Format.Format_RGB888)
        return qimg

    def process(self):
        self.rec_scene.clear()
        self.calculate_sfr()
        show_image = self.draw_result(self.image_8bit)
        show_image = self.cv2qimg(show_image)
        rec_item = QGraphicsPixmapItem(QPixmap(show_image))
        rec_item.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.rec_scene.addItem(rec_item)
        self.rec_view.fitInView(rec_item, Qt.AspectRatioMode.KeepAspectRatio)

    def save_result(self):
        if self.cap_win.isHidden():
            QMessageBox.critical(self.window, '错误', '未进行捕获识别，保存前请打开识别', QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
        else:
            result = self.draw_result(self.image_8bit)
            self.save_img(result, format("result-" + time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime())))

# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = camera()
    ui.window.show()
    sys.exit(app.exec())

