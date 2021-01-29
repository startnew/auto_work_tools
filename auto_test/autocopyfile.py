#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/11/13 17:49
# @Author  : zhuzhaowen
# @email   : shaowen5011@gmail.com
# @File    : autocopyfile.py
# @Software: PyCharm
# @desc    : ""

import os

while True:
    p = r"C:\Windows\LVUAAgentInstBaseRoot\personal\LVPReportScreenVT.cache.arc"
    p_l = r"C:\Users\zhuzhaowen\Desktop\1(1)\t.arc"
    if os.path.exists(p):
        with open(p,"rb") as fl:
            s = fl.read()
        with open(p_l,"wb") as fl2:
            fl2.write(s)
            print("写入成功break")
            break
    else:
        continue