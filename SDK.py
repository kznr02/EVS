from typing import Union, Any

import cv2
import time
import os
import numpy as np
from PIL import Image
from ctypes import *
from GPCAlgo.CAlgoAAMeasurement import CAlgoAAMeasurement

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
        self.save_img(amp_data, '0.png')

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

    def draw_result(self, src: np.ndarray) -> Any:
        aa_image_path = os.path.join(self.res_path, '0.png')
        aa_image = cv2.imread(aa_image_path)
        aa_image_gray = cv2.cvtColor(aa_image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(aa_image_gray, 180, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        contours, hierachy = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_L1)
        for cnt in contours:
            rect = cv2.minAreaRect(cnt)
            box = np.int_(cv2.boxPoints(rect))

            cv2.drawContours(aa_image, [box], 0, (0, 255, 0), 2)
        return binary

    def sdk_version(self) -> str:
        self.sdk.api_get_sdk_ver.restype = c_char_p
        ver_str = self.sdk.api_get_sdk_ver()
        return ver_str.decode("utf-8")
