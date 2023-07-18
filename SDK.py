from typing import Union, Any

import cv2
import time
import os
import numpy as np
from PIL import Image
from ctypes import *
from GPCAlgo.CAlgoAAMeasurement import CAlgoAAMeasurement

BOX_WIDTH = 40
BOX_THICKNESS = 2

class SRC_IMG(Structure):
    _fields_ = [("type", c_int), ("len", c_int), ("data", POINTER(c_uint16))]


class SRC_ALL(Structure):
    _fields_ = [("rgb", SRC_IMG), ("amp", SRC_IMG), ("depth", SRC_IMG)]

class sdk():
    def __init__(self):
        # 路径定义
        self.sdk_path = r"./SDK"
        self.res_path = r"./result"
        self.result_c_image_path = os.path.join(self.res_path, 'result_AA_measurement', '0_C.png')
        self.result_dl_image_path = os.path.join(self.res_path, 'result_AA_measurement', '0_DL.png')
        self.result_dr_image_path = os.path.join(self.res_path, 'result_AA_measurement', '0_DR.png')
        self.result_ul_image_path = os.path.join(self.res_path, 'result_AA_measurement', '0_UL.png')
        self.result_ur_image_path = os.path.join(self.res_path, 'result_AA_measurement', '0_UR.png')
        # 导入库文件
        self.lib_path = os.path.join(self.sdk_path, "lib", "SDK_WIN.dll")
        self.sdk = cdll.LoadLibrary(self.lib_path)
        # 初始化库
        self.sdk.api_init()
        # 建立相机句柄
        self.cam_handle = None
        # 创建图片变量
        self.img = None
        # 定义帧数
        self.frame_count = 1
        # 配置文件路径
        self.config_file_folder = "AA_measurement_calgo_config.json"

    def connect_cam(self, host: bytes, port: int):
        self.cam_handle = self.sdk.api_connect(host, port)

    def disconnect_cam(self):
        self.sdk.api_disconnect(self.cam_handle)
    def get_frame(self) -> Any:
        self.sdk.api_get_img.restype = POINTER(SRC_ALL)

        while True:
            self.img = self.sdk.api_get_img(self.cam_handle)
            if self.img:
                break
            time.sleep(0.01)
        return self.img

    def conv16to8(self, src: np.ndarray) -> Any:
        src -= src.min()
        amp_data = src / (src.max() - src.min())
        amp_data *= 255
        amp_data = amp_data.astype('uint8')
        return amp_data

    def process_img_data(self, src: np.ndarray) -> Any:
        # 计算照片数据
        img_length = src.contents.depth.len // 2
        amp_data = np.array(src.contents.amp.data[:img_length]).reshape(480, 640).astype(np.uint16)
        # 16bit 2 8bit
        amp_data = self.conv16to8(amp_data)
        # self.save_img(amp_data, '0.png')

        return amp_data

    def save_img(self, src: np.ndarray, name: str):
        # 存图
        amp_image = Image.fromarray(src)
        amp_image_path = os.path.join(self.res_path, name)
        amp_image.save(amp_image_path)

    def calculate_sfr(self):
        aa_image_path = os.path.join(self.res_path, '0.png')
        aa_image = cv2.imread(aa_image_path)
        if aa_image is not None:
            result = {}
            a = CAlgoAAMeasurement(self.config_file_folder, result)
            data_result_folder = "result"
            result = a.is_success(data_result_folder)
            print(result)

    def draw_result(self, src) -> Any:
        aa_image_path = os.path.join(self.res_path, '0.png')
        aa_image = cv2.imread(aa_image_path)
        aa_image_gray = cv2.cvtColor(aa_image, cv2.COLOR_BGR2GRAY)

        edge = cv2.Canny(aa_image_gray, 255, 0)
        corners = cv2.goodFeaturesToTrack(edge, 1000, 0.01, 60)

        plist = []
        for i in range(0, 20):
            x_o = int(corners[i][0][0])
            y_o = int(corners[i][0][1])
            plist.append((x_o, y_o))
        plist.sort(key=lambda elem: elem[0])

        plist_left = []
        for i in range(0, 8):
            plist_left.append(plist[i])
        plist_left.sort(key=lambda elem: elem[1])
        # print("left: ", plist_left)
        left_points = [
            ((plist_left[0][0] + plist_left[1][0]) // 2, (plist_left[0][1] + plist_left[1][1]) // 2),
            ((plist_left[0][0] + plist_left[2][0]) // 2, (plist_left[0][1] + plist_left[2][1]) // 2),
            ((plist_left[3][0] + plist_left[1][0]) // 2, (plist_left[3][1] + plist_left[1][1]) // 2),
            ((plist_left[3][0] + plist_left[2][0]) // 2, (plist_left[3][1] + plist_left[2][1]) // 2),
            ((plist_left[4][0] + plist_left[5][0]) // 2, (plist_left[4][1] + plist_left[5][1]) // 2),
            ((plist_left[4][0] + plist_left[6][0]) // 2, (plist_left[4][1] + plist_left[6][1]) // 2),
            ((plist_left[7][0] + plist_left[5][0]) // 2, (plist_left[7][1] + plist_left[5][1]) // 2),
            ((plist_left[7][0] + plist_left[6][0]) // 2, (plist_left[7][1] + plist_left[6][1]) // 2)
        ]
        for i in left_points:
            cv2.rectangle(aa_image, (i[0] - BOX_WIDTH, i[1] - BOX_WIDTH), (i[0] + BOX_WIDTH, i[1] + BOX_WIDTH), (0, 0, 255),
                          BOX_THICKNESS)

        plist_center = []
        for i in range(8, 12):
            plist_center.append(plist[i])
        plist_center.sort(key=lambda elem: elem[1])
        # print("center: ", plist_center)
        center_points = [
            ((plist_center[0][0] + plist_center[1][0]) // 2, (plist_center[0][1] + plist_center[1][1]) // 2),
            ((plist_center[0][0] + plist_center[2][0]) // 2, (plist_center[0][1] + plist_center[2][1]) // 2),
            ((plist_center[3][0] + plist_center[1][0]) // 2, (plist_center[3][1] + plist_center[1][1]) // 2),
            ((plist_center[3][0] + plist_center[2][0]) // 2, (plist_center[2][1] + plist_center[2][1]) // 2)
        ]
        for i in center_points:
            cv2.rectangle(aa_image, (i[0] - BOX_WIDTH, i[1] - BOX_WIDTH), (i[0] + BOX_WIDTH, i[1] + BOX_WIDTH), (0, 0, 255),
                          BOX_THICKNESS)

        plist_right = []
        for i in range(12, 20):
            plist_right.append(plist[i])
        # print("right: ", plist_right)
        plist_right.sort(key=lambda elem: elem[1])
        right_points = [
            ((plist_right[0][0] + plist_right[1][0]) // 2, (plist_right[0][1] + plist_right[1][1]) // 2),
            ((plist_right[0][0] + plist_right[2][0]) // 2, (plist_right[0][1] + plist_right[2][1]) // 2),
            ((plist_right[3][0] + plist_right[1][0]) // 2, (plist_right[3][1] + plist_right[1][1]) // 2),
            ((plist_right[3][0] + plist_right[2][0]) // 2, (plist_right[3][1] + plist_right[2][1]) // 2),
            ((plist_right[4][0] + plist_right[5][0]) // 2, (plist_right[4][1] + plist_right[5][1]) // 2),
            ((plist_right[4][0] + plist_right[6][0]) // 2, (plist_right[4][1] + plist_right[6][1]) // 2),
            ((plist_right[7][0] + plist_right[5][0]) // 2, (plist_right[7][1] + plist_right[5][1]) // 2),
            ((plist_right[7][0] + plist_right[6][0]) // 2, (plist_right[7][1] + plist_right[6][1]) // 2)
        ]
        for i in right_points:
            cv2.rectangle(aa_image, (i[0] - BOX_WIDTH, i[1] - BOX_WIDTH), (i[0] + BOX_WIDTH, i[1] + BOX_WIDTH), (0, 0, 255),
                          BOX_THICKNESS)

        UL_box_points = []
        DL_box_points = []
        CT_box_points = []
        UR_box_points = []
        DR_box_points = []
        for i in range(0, 4):
            UL_box_points.append(plist_left[i])
            DL_box_points.append(plist_left[i + 4])
            CT_box_points.append(plist_center[i])
            UR_box_points.append(plist_right[i])
            DR_box_points.append(plist_right[i + 4])
        UL_center_point = \
            ((((UL_box_points[0][0] + UL_box_points[3][0]) // 2) + (
                        (UL_box_points[1][0] + UL_box_points[2][0]) // 2)) // 2,
             (((UL_box_points[0][1] + UL_box_points[3][1]) // 2) + (
                         (UL_box_points[1][1] + UL_box_points[2][1]) // 2)) // 2)
        DL_center_point = \
            ((((DL_box_points[0][0] + DL_box_points[3][0]) // 2) + (
                        (DL_box_points[1][0] + DL_box_points[2][0]) // 2)) // 2,
             (((DL_box_points[0][1] + DL_box_points[3][1]) // 2) + (
                         (DL_box_points[1][1] + DL_box_points[2][1]) // 2)) // 2)
        CT_center_point = \
            ((((CT_box_points[0][0] + CT_box_points[3][0]) // 2) + (
                        (CT_box_points[1][0] + CT_box_points[2][0]) // 2)) // 2,
             (((CT_box_points[0][1] + CT_box_points[3][1]) // 2) + (
                         (CT_box_points[1][1] + CT_box_points[2][1]) // 2)) // 2)
        UR_center_point = \
            ((((UR_box_points[0][0] + UR_box_points[3][0]) // 2) + (
                        (UR_box_points[1][0] + UR_box_points[2][0]) // 2)) // 2,
             (((UR_box_points[0][1] + UR_box_points[3][1]) // 2) + (
                         (UR_box_points[1][1] + UR_box_points[2][1]) // 2)) // 2)
        DR_center_point = \
            ((((DR_box_points[0][0] + DR_box_points[3][0]) // 2) + (
                        (DR_box_points[1][0] + DR_box_points[2][0]) // 2)) // 2,
             (((DR_box_points[0][1] + DR_box_points[3][1]) // 2) + (
                         (DR_box_points[1][1] + DR_box_points[2][1]) // 2)) // 2)

        return aa_image

    def sdk_version(self) -> str:
        self.sdk.api_get_sdk_ver.restype = c_char_p
        ver_str = self.sdk.api_get_sdk_ver()
        return ver_str.decode("utf-8")
