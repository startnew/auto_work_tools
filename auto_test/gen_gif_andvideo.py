#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/29 16:03
# @Author  : zhuzhaowen
# @email   : shaowen5011@gmail.com
# @File    : gen_gif_andvideo.py
# @Software: PyCharm
# @desc    : "在当前目录下根据图片自动生成gif 图片与视频"


from PIL import Image
import numpy as np
import imageio
import os


def imgs2mp4(imgs, filename, w, h, fps=3, ):
    print("imgs {}".format(len(imgs)))
    filename_ = filename + ".mp4"
    shape = [w, h]
    imgs_ = []

    with imageio.get_writer(filename_, fps=fps) as video:
        for i, img in enumerate(imgs):
            img_data = np.array(img, dtype=np.uint8)
            img_data = Image.fromarray(img_data)
            img_data = img_data.resize(shape)
            img_data = np.array(img_data)
            imgs_.append(img_data)
            video.append_data(img_data)
    print("save path:{}".format(filename_))
    filename_ = filename + ".gif"
    imageio.mimsave(filename_, imgs_, fps=fps)
    return filename_


import pyautogui

if __name__ == '__main__':

    s = pyautogui.confirm('组合当前目录下的jpg 与 png 文件形成gif与mp4')
    s = pyautogui.prompt("请输入图片归一化构成的分辨率默认为{}x{},如不需要更改请按ok,".format(480 * 4, 270 * 4))
    if len(s) > 0:
        w, h = s.split("x")
        w, h = int(w), int(h)
    else:
        w, h = 480 * 4, 270 * 4
    fps = 3
    s = pyautogui.prompt("请输入fps默认为{},".format(3))

    if len(s) > 0:
        fps = int(s)
    paths = []
    imgs = []
    for root, dirs, files in os.walk("./"):
        for name in files:
            if name.endswith(".jpg") or name.endswith(".png") or name.endswith(".jpeg"):
                k = os.path.join(root, name)
                paths.append(k)
    paths.sort()
    for path in paths:
        image = Image.open(path)
        image = np.array(image.resize([w, h], resample=0))
        imgs.append(image)
    imgs2mp4(imgs, "result", w, h, fps=fps)
    pyautogui.confirm('文件保存在当前目录下的result.mp4,result.gif')