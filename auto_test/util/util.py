#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/11/9 14:50
# @Author  : zhuzhaowen
# @email   : shaowen5011@gmail.com
# @File    : util.py
# @Software: PyCharm
# @desc    : ""
import time
def exc_time(func):
    def new_func(*args, **args2):
        t0 = time.time()
        # print("@ {},{} start".format(time.strftime("%X", time.localtime()), func.__name__))
        back = func(*args, **args2)
        # print("@ {}, {} end".format(time.strftime("%X", time.localtime()), func.__name__))
        print("@ {} taken for {}".format(time.time() - t0, func.__name__))
        return back

    return new_func


import cv2
import base64
import numpy as np


def image_to_base64(image_np):
    """
    图片转换为 base64
    :param image_np:
    :return:
    """
    image = cv2.imencode('.jpg', image_np)[1]
    image_code = str(base64.b64encode(image))[2:-1]
    return image_code


def base64_to_image(base64_code):
    """
    base64转换为图片
    :param base64_code:
    :return:
    """
    # base64解码
    img_data = base64.b64decode(base64_code)
    # 转换为np数组
    img_array = np.fromstring(img_data, np.uint8)
    # 转换成opencv可用格式
    img = cv2.imdecode(img_array, cv2.COLOR_RGB2BGR)
    return img


class ProviceMap():

    def __init__(self):
        pass



