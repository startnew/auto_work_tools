#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/11/4 15:37
# @Author  : zhuzhaowen
# @email   : shaowen5011@gmail.com
# @File    : autotestlabel.py
# @Software: PyCharm
# @desc    : "自动查看标注结果web"



import pyautogui
pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = True
import numpy as np
from PIL import Image
import time

width,height = pyautogui.size()
print(width,height)
x,y = pyautogui.position()
print("x,y",x,y)

s = pyautogui.confirm('是否已将标注web界面打开，并最大化到主屏幕上，继续请确认 退出点击取消')
if s == "OK":

    print(s, type(s))
    # 点击下一张


else:
    exit()
speed = pyautogui.prompt('请输入每次点击的速度 s 如 0.3 s 使用过程中请不要移动你的鼠标')
speed = float(speed)
print("x,y",x,y)


pyautogui.screenshot('foo.png')


for i in range(100):


    time.sleep(2)
    pyautogui.moveTo(1686, 467, duration=0.25)
    pyautogui.scroll(3000)


    for k in range(70):

        pyautogui.moveTo(1686, 467, duration=0.25)
        for j in range(3):
            pyautogui.click(button="left")
            time.sleep(speed)
        print("scroll")
        r_b = pyautogui.screenshot()
        before_img = np.array(r_b)
        pyautogui.scroll(-30)

        r_n = pyautogui.screenshot()
        now_img = np.array(r_n)

        if (now_img == before_img).all() :
            print("滚动后无变化自动跳出")
            print(r_n==r_b)

            break
        else:
            r_b = r_n
            before_img = now_img

        #break
    for k in range(11):
        if k == 0:
            for j in range(3):
                pyautogui.click(button="left")
                time.sleep(speed)

        else:
            r_b = pyautogui.screenshot()
            before_img = np.array(r_b)

            pyautogui.moveTo(1679, 467 + k * (25), duration=0.55)
            for j in range(3):
                pyautogui.click(button="left")
                time.sleep(speed)



            r_n = pyautogui.screenshot()
            now_img = np.array(r_n)

            if (now_img == before_img).all() or k > 34:
                print("滚动后无变化自动跳出")
                print(r_n == r_b)

                break
            else:
                r_b = r_n
                before_img = now_img

        # pyautogui.moveTo(1686, 467 + k * (26), duration=0.55)
        # for j in range(3):
        #     pyautogui.click(button="left")
        #     time.sleep(0.1)

    x,y = pyautogui.position()
    print("当前鼠标的位置:{},{}".format(x,y))

    #pyautogui.alert('是否进行下一张图片')
    s = pyautogui.confirm('是否进行下一张图片')
    if s == "OK":

        print(s,type(s))
        # 点击下一张
        pyautogui.moveTo(1175, 1030, duration=0.5)
        pyautogui.click(button="left")
    else:
        break
#
#     break
#     # pyautogui.click(button="left")
#     # pyautogui.click(button="middle")
#     # pyautogui.scroll(200)
#     # pyautogui.scroll(-200)
#     # pyautogui.moveTo(1000, 30, duration=0.25)