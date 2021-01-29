#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/9/2 17:35
# @Author  : zhuzhaowen
# @email   : shaowen5011@gmail.com
# @File    : auto_click_chrome_colab.py
# @Software: PyCharm
# @desc    : "自动点击屏幕中的colab 不让它断开"
import pyautogui
pyautogui.PAUSE = 3
pyautogui.FAILSAFE = True
width,height = pyautogui.size()
print(width,height)

for i in range(1000):
    #pyautogui.moveTo(300, 300, duration=0.25)
    #pyautogui.moveTo(400, 300, duration=0.25)
    #pyautogui.moveTo(400, 400, duration=0.25)
    pyautogui.moveTo(800, 150, duration=0.25)
    x,y = pyautogui.position()
    print("当前鼠标的位置:{},{}".format(x,y))
    pyautogui.click(button="left")
    pyautogui.click(button="middle")
    pyautogui.scroll(200)
    pyautogui.scroll(-200)
    pyautogui.moveTo(1000, 30, duration=0.25)