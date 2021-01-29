#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/11/6 15:42
# @Author  : zhuzhaowen
# @email   : shaowen5011@gmail.com
# @File    : auto_upload_img_2_dr.py
# @Software: PyCharm
# @desc    : "通过界面操作的方式批量导入户型图到DR软件中"

import pyautogui
import pyperclip
import threading
import imageio
from PIL import Image

pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = False
import numpy as np
from PIL import Image
import time
import os
import pandas as pd
from util.util import base64_to_image
import pickle
import cv2
from tqdm import tqdm

global imgs
imgs = []

record = False

use_sqllite = True
if use_sqllite:
    import sqlite3

    if os.path.exists("status.db"):
        conn = sqlite3.connect("status.db")
        cursor = conn.cursor()
    else:
        conn = sqlite3.connect("status.db")
        cursor = conn.cursor()
        # "cityname", "楼盘", "区", "户型图"
        cursor.execute(
            'create table status (id integer primary key autoincrement,cityname varchar(10),loupan varchar(10),contyname varchar(10),imgurl varchar(64) UNIQUE, status integer )')


class DRStartThread(threading.Thread):
    def __init__(self, threadID, name="打开DR软件", DR_PATH=''):
        threading.Thread.__init__(self)
        self.__flag = threading.Event()
        self.__flag.set()  # 设置为True
        self.__running = threading.Event()  # 用于停止线程的标识
        self.__running.set()
        self.threadID = threadID
        self.name = name
        self.dr_path = DR_PATH

    def run(self):
        print("开始线程:" + self.name)
        print(self.dr_path)
        os.system(self.dr_path)

    def stop(self):
        st = time.time()
        f = os.popen("tasklist | findstr Drama")
        for line in f.readlines():
            infos = line.split()
            print(infos)
            pid = infos[1]
            os.system("taskkill /pid {} -t -f".format(pid))
        ed = time.time()
        print("STOP DR use {}".format(ed - st))
        # print("f:{}".format(f.readlines()[0].split()))


class DRShutDownThread(threading.Thread):
    def __init__(self, threadID, name="打开DR软件", DR_PATH=''):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.dr_path = DR_PATH

    def run(self):
        print("开始线程:" + self.name)
        os.system(self.dr_path)


class Upload2DR():
    def __init__(self, pause, DR_PATH=""):
        self.pause = pause
        self.set_pause(pause)
        self.dr_path = DR_PATH

    def shutdownDr(self):

        pass

    def startDr(self):

        thread1 = DRStartThread(1, "打开dr软件", self.dr_path)
        thread1.start()
        self.drthread = thread1

    def shutdownDr(self):
        self.drthread.stop()

    def restartDr(self):
        print("重启DR 软件")
        self.shutdownDr()
        time.sleep(1)
        self.startAndLoggin()
        time.sleep(3)
        self.clickHouseLib()
        time.sleep(3)

    def clickHouseLib(self):
        pos = self.getHouseLibButtonPos()

        self.moveAndClick(pos)
        time.sleep(1)

    def startAndLoggin(self):
        self.startDr()
        time.sleep(8)
        self.loggin()
        addrecords()

    def loggin(self):
        time.sleep(0.5)
        pos = self.getDrLoginSubmitLoc()
        self.moveAndClick(pos)
        time.sleep(0.5)

    def actionCreateNewHouse(self, data):
        ''':param创建新户型的动作'''

        house_name = data.get("house_name")
        county_name = data.get("county_name")
        community_name = data.get("community_name")
        print("户型名:{} 区县:{} 小区名称:{}".format(house_name, county_name, community_name))

        pos = self.getCreateHousePos()
        self.moveTo(pos)
        r_b = pyautogui.screenshot()
        before_img = np.array(r_b)

        self.moveAndClick(pos)
        time.sleep(12)
        r_n = pyautogui.screenshot()
        now_img = np.array(r_n)
        if (now_img == before_img).all():
            print("点击新建户型后无变化自动跳出")
            print(r_n == r_b)
            r_n = pyautogui.screenshot()
            now_img = np.array(r_n)
            time.sleep(15)
            if (now_img == before_img).all():
                print("点击新建户型后无变化自动跳出")
                print(r_n == r_b)
                return "RESTART"

        r_b = pyautogui.screenshot()
        before_img = np.array(r_b)
        pos = self.getHouseInputNamePos()
        self.moveAndClick(pos)
        self.writeWords(house_name)  # ("117平米户型")
        r_n = pyautogui.screenshot()
        now_img = np.array(r_n)
        if (now_img == before_img).all():
            print("写入户型后无变化自动跳出")
            print(r_n == r_b)
            return "RESTART"

        r_b = pyautogui.screenshot()
        before_img = np.array(r_b)

        pos = self.getHouseLocatePos()
        self.moveAndClick(pos)
        pos = self.getSelectProvincePos()
        self.moveAndClick(pos)

        if "南京" in data.get("cityname"):
            p_pos = self.getHouseLocJS()
        else:
            posDicts = self.getHouseLocDict()
            previces = [x for x in posDicts if x["name"] == data.get("pname")]
            if len(previces) == 0:
                print("配置中没有该省份信息 请更新配置:{}".format(data.get("pname")))
                return "NOT CONFIG PROVICENCE NAME LOC POS"
            else:
                print(previces[0]["name"])
                p_pos = previces[0]["pos"]

        self.moveAndClick(p_pos)

        pos = self.getSelectCityPos()
        self.moveAndClick(pos)
        if "南京" in data.get("cityname"):
            c_pos = self.getHouseLocNJ()
        else:
            citys = [x for x in previces[0]["citys"] if x["name"] == data.get("cityname")]
            if len(citys) == 0:
                print("配置中没有该城市信息 请更新配置:{}".format(data.get("cityname")))
                return "NOT CONFIG CITY NAME LOC POS"
            else:
                print(citys[0]["name"])
                c_pos = citys[0]["pos"]
        self.moveAndClick(c_pos)

        pos = self.getSelectCountyPos()
        self.moveAndClick(pos)

        if "南京" in data.get("cityname"):

            poses = self.getHouseCountyLocs()
            county_pos = poses[county_name]
        else:
            countys = [x for x in citys[0]["countys"] if x["name"] == data.get("county_name")]
            if len(countys) == 0:
                print("配置中没有该区县信息 请更新配置:{}".format(data.get("county_name")))
                return "NOT CONFIG county NAME LOC POS"
            else:
                print(countys[0]["name"])
                county_pos = countys[0]["pos"]

        self.moveAndClick(county_pos)
        pos = self.getHouseCommunityNameLoc()
        self.moveAndClick(pos)
        self.writeWords(community_name)
        pyautogui.press("enter")

        pos = self.getclickConmunityNameLoc()
        self.moveAndClick(pos)
        r_n = pyautogui.screenshot()
        now_img = np.array(r_n)
        if (now_img == before_img).all():
            print("点击加入户型信息后户型后无变化自动跳出")
            print(r_n == r_b)
            return "RESTART"

        pos = self.getHouseAuthPubSetLoc()
        # self.moveAndClick(pos)

        pos = self.getConfirmButtonLoc()
        self.moveAndClick(pos)

        return "OK"

    def actionImportImage(self, imgpath, name="./result/k.png"):
        # pos = self.getSelectFilePathLoc()
        # self.moveAndClick(pos)
        # pyautogui.press("tab", presses=5, interval=0.2)
        # pyautogui.press('enter')
        # pyautogui.press('delete')

        dirname = os.path.dirname(imgpath)
        print("dirname{}".format(dirname))
        ori_imgpath = self.normWindowsPath(imgpath)
        print("imgpath", self.normWindowsPath(imgpath))
        self.writeWords(self.normWindowsPath(imgpath))
        time.sleep(1)
        # pyautogui.press('enter')
        # pyautogui.press("tab", presses=5, interval=0.2)
        # pyautogui.press('down')
        pyautogui.hotkey('alt', "o")
        # pos = self.getImgPathLoc()
        # self.moveAndClick(pos)

        # pos = self.getImgPathConfirmButtonLoc()
        # self.moveAndClick(pos)

        time.sleep(2)

        pos = self.getImgRecButtonLoc()
        time.sleep(2)

        self.moveTo(pos)
        r_b = pyautogui.screenshot()
        before_img = np.array(r_b)
        self.moveAndClick(pos)
        time.sleep(20)
        r_n = pyautogui.screenshot()
        now_img = np.array(r_n)
        if (now_img == before_img).all():
            print("识别户型后无变化自动跳出")
            print(r_n == r_b)
            return "RESTART"

        pos = self.getHouseSaveButtonLoc()

        self.moveAndClick(pos)

        time.sleep(5)

        path = os.path.dirname(name)
        os.makedirs(path, exist_ok=True)
        self.moveAndClick(pos)
        pyautogui.scroll(-20)
        pyautogui.scroll(-1500)
        pos = self.getscalePos()
        self.moveAndClick(pos)
        print("截屏保存位置screenshot save at :{}".format(name))
        with open(ori_imgpath, "rb") as f1:
            s = name.split(".")
            s[-1] = "_ori." + s[-1]
            ori_name = ".".join(s)
            with open(ori_name, "wb") as f2:
                f2.write(f1.read())
        if record:
            imgs.append(np.array(Image.open(ori_imgpath)))

        pyautogui.screenshot('{}'.format(name))
        pos = self.getGoUperButtonLoc()
        self.moveAndClick(pos)

        pos = self.getConfirmExitButtonLoc()
        self.moveTo(pos)
        r_b = pyautogui.screenshot()
        before_img = np.array(r_b)
        self.moveAndClick(pos)

        time.sleep(2)
        r_n = pyautogui.screenshot()
        now_img = np.array(r_n)
        if (now_img == before_img).all():
            print("识别户型后无变化自动跳出")
            print(r_n == r_b)
            return "RESTART"
        if record:
            imgs2mp4(imgs, name.replace(".png", ""), fps=5)
        cleanrecords(imgs)
        return "OK"

    def writeWords(self, words):
        pyperclip.copy(words)
        print("写入字符", words)
        # pyperclip.paste()

        pyautogui.hotkey("ctrl", "v")

    def normWindowsPath(self, path):
        '''标准化为windows的视图与路径:param'''
        path = path.replace("/", "\\")
        path = path.replace("\\\\", "\\")
        print(path)
        return path

    def getHouseLibButtonPos(self):
        a = [438, 81]
        return {"x": a[0], "y": a[1]}

    def getscalePos(self):
        a = [435, 1020]
        return {"x": a[0], "y": a[1]}

    def getCreateHousePos(self):
        a = [1771, 158]
        return {"x": a[0], "y": a[1]}

    def getHouseInputNamePos(self):
        '''获取 输入 户型名称 的 屏幕坐标点:param'''
        return {"x": 924, "y": 459}

    def getHouseLocatePos(self):
        '''获取 输入 所在地区 的 屏幕坐标点:param'''
        return {"x": 981, "y": 500}

    def getSelectProvincePos(self):
        '''
        获取选择省的位置
        :return:
        '''
        a = [910, 545]
        return {"x": a[0], "y": a[1]}

    def getSelectCityPos(self):
        '''
        获取选择城市的位置
        :return:
        '''
        a = [999, 542]
        return {"x": a[0], "y": a[1]}

    def getSelectCountyPos(self):
        '''
        获取选择城市的位置
        :return:
        '''
        a = [1099, 542]
        return {"x": a[0], "y": a[1]}

    def getHouseLocJS(self):
        '''获取 输入 江苏省 的 屏幕坐标点:param'''
        a = [1097, 616]
        return {"x": a[0], "y": a[1]}

    def getHouseLocNJ(self):
        '''获取 输入 南京 的 屏幕坐标点:param'''
        a = [1038, 574]
        return {"x": a[0], "y": a[1]}

    def getHouseCommunityNameLoc(self):
        '''获取小区名称的位置:param'''
        a = [978, 547]
        return {"x": a[0], "y": a[1]}

    def getDrLoginSubmitLoc(self):
        a = [962, 645]
        return {"x": a[0], "y": a[1]}

    def getclickConmunityNameLoc(self):
        a = [786, 553]
        return {"x": a[0], "y": a[1]}

    def getHouseAuthPubSetLoc(self):
        '''获取共享权限设置的位置:param'''
        a = [870, 593]
        return {"x": a[0], "y": a[1]}

    def getSelectFilePathLoc(self):
        '''点击文件路径的位置：param'''
        a = [857, 180]
        return {"x": a[0], "y": a[1]}

    def getImgPathLoc(self):
        '''点击图片的位置：param'''
        a = [605, 278]
        return {"x": a[0], "y": a[1]}

    def getImgPathConfirmButtonLoc(self):
        '''点击图片的打开按钮：param'''
        a = [1067, 632]
        return {"x": a[0], "y": a[1]}

    def getImgRecButtonLoc(self):
        '''点击确定使用户型图识别按钮：param'''
        a = [894, 594]
        return {"x": a[0], "y": a[1]}

    def getHouseSaveButtonLoc(self):
        '''保存户型图的按钮：param'''
        a = [44, 60]
        return {"x": a[0], "y": a[1]}

    def getGoUperButtonLoc(self):
        '''退出户型编辑的按钮位置：param'''
        a = [1877, 66]
        return {"x": a[0], "y": a[1]}

    def getConfirmExitButtonLoc(self):
        '''返回确认退回按钮的位置:param'''
        a = [953, 520]
        return {"x": a[0], "y": a[1]}

    def getConfirmButtonLoc(self):
        '''获取点击确定的位置:param'''
        a = [995, 662]
        return {"x": a[0], "y": a[1]}

    def getHouseCountyLocs(self):
        '''获取 输入 各个区县 的 屏幕坐标点:param'''
        res = {}
        names = ["白下区", "下关区", "浦口区", "雨花台区", "江宁区", "溧水区", "六合区", "高淳区", "建邺区", "鼓楼区", "秦淮区",
                 "栖霞区", "玄武区"]
        poss = [[894, 579], [964, 575], [1015, 573], [1106, 581], [884, 625], [960, 618], [1031, 613], [1120, 617],
                [893, 654], [961, 658],
                [1034, 659], [1115, 657], [884, 695]]
        for i, name in enumerate(names):
            a = poss[i]
            res[name] = {"x": a[0], "y": a[1]}
        return res

    def getHouseLocDict(self):
        provices = []

        henan = {}
        henan["pos"] = {"x": 966, "y": 701}
        henan["name"] = "河南省"

        names = ["洛阳市", "三门峡市", "漯河市", "许昌市", "南阳市", "信阳市", "济源市", "驻马店市", "濮阳市", "焦作市",
                 "郑州市", "安阳市", "新乡市", "鹤壁市",
                 "开封市", "周口市", "平顶山市", "商丘市"]

        startpos = [892, 583]
        colum_abs_dis = 70
        row_abs_dis = 40
        citys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis, max_col=4)
        henan["citys"] = citys

        for city in citys:
            if city["name"] == "洛阳市":
                names = ["高新技术开发区", "经济技术开发区", "新安县", "栾川县", "伊川县", "吉利区", "洛宁县", "偃师市",
                         "瀍河回族区", "老城区", "西工区", "孟津县",
                         "洛龙区", "涧西区", "宜阳县", "汝阳县", "嵩县"]
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis, max_col=4,
                                            skips={0: 2, 1: 2, 8: 2})
                city["countys"] = contys

            if city["name"] == "信阳市":
                names = ["潢川县", "淮滨县", "罗山县", "光山县", "新县", "浉河区", "固始县", "商城县", "息县", "平桥区"]
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis, max_col=4,
                                            skips={})
                city["countys"] = contys

            if city["name"] == "三门峡市":
                names = ["陕县", "湖滨区", "卢氏县", "渑池县", "灵宝县", "陕州区", "义马市"]
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis, max_col=4,
                                            )
                city["countys"] = contys

            if city["name"] == "漯河市":
                names = ["召陵区", "临颍县", "源汇区", "郾城区", "舞阳县"]
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis,
                                            max_col=4,
                                            )
                city["countys"] = contys

            if city["name"] == "许昌市":
                names = ["许昌县", "建安区", "魏都区", "长葛市", "禹州市", "鄢陵县", "襄城县"]
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis,
                                            max_col=4,
                                            )
                city["countys"] = contys

            if city["name"] == "南阳市":
                names = ["西峡县", "社旗县", "桐柏县", "卧龙区", "南召县", "唐河县", "方城县", "宛城区", "新野县",
                         "镇平县", "淅川县", "邓州市", "内乡县"]
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis,
                                            max_col=4,
                                            )
                city["countys"] = contys

            if city["name"] == "济源市":
                names = ["济源县"]
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis,
                                            max_col=4,
                                            )
                city["countys"] = contys

            if city["name"] == "驻马店市":
                names = ["上蔡县", "西平县", "新蔡县", "泌阳县", "驿城区", "确山县", "正阳县", "遂平县", "汝南县", "平舆县"]
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis,
                                            max_col=4,
                                            )
                city["countys"] = contys

            if city["name"] == "濮阳市":
                names = ["台前县", "南乐县", "范县", "华龙区", "清丰县", "濮阳县"]
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis,
                                            max_col=4,
                                            )
                city["countys"] = contys

            if city["name"] == "焦作市":
                names = ["孟州市", "温县", "沁阳市", "马村区", "武陟县", "博爱县", "修武县", "解放区", "山阳区", "中站区"]
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis,
                                            max_col=4,
                                            )
                city["countys"] = contys

            if city["name"] == "郑州市":
                names = ["高新技术开发区", "经济技术开发区", "郑东新区", "出口加工区", "登封市", "中原区", "新密市", "新郑市", "巩义市", "荥阳市", "上街区", "二七区",
                         "金水区", "惠济区", "中牟县", "管城回族区"]
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis,
                                            max_col=4, skips={0: 2, 1: 2, 3: 2}
                                            )
                city["countys"] = contys

            if city["name"] == "安阳市":
                names = ["汤阴县", "殷都区", "林州市", "龙安区", "内黄县", "北关区", "安阳县", "文峰区", "滑县"]
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis,
                                            max_col=4, skips={}
                                            )
                city["countys"] = contys

            if city["name"] == "新乡市":
                names = ["辉县市", "凤泉区", "长垣市", "牧野区", "卫滨区", "获嘉县", "新乡县", "封丘县", "原阳县", "延津县", "卫辉市", "红旗区"]
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis,
                                            max_col=4, skips={}
                                            )
                city["countys"] = contys

            if city["name"] == "鹤壁市":
                names = ["鹤山区", "山城区", "淇县", "淇滨区", "浚县"]
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis,
                                            max_col=4, skips={}
                                            )
                city["countys"] = contys

            if city["name"] == "开封市":
                names = ["开封县", "金明区", "顺河回族区", "祥符区", "禹王台区", "龙亭区", "尉氏县", "兰考县", "杞县", "通许县", "鼓楼区"]
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis,
                                            max_col=4, skips={2: 2}
                                            )
                city["countys"] = contys

            if city["name"] == "周口市":
                names = ["沈丘县", "项城市", "川汇区", "商水县", "鹿邑县", "郸城县", "淮阳区", "西华县", "扶沟县", "太康县"]
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis,
                                            max_col=4, skips={}
                                            )
                city["countys"] = contys

            if city["name"] == "平顶山市":
                names = ["石龙区", "卫东区", "鲁山县", "湛河区", "舞钢市", "郏县", "叶县", "宝丰县", "汝州市", "新华区"]
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis,
                                            max_col=4, skips={}
                                            )
                city["countys"] = contys

            if city["name"] == "商丘市":
                names = ["宁陵县", "梁园区", "永城市", "睢阳区", "睢县", "夏邑县", "虞城县", "民权县", "柘城县"]
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis,
                                            max_col=4, skips={}
                                            )
                city["countys"] = contys
                # self.judgePos(contys)

        provices.append(henan)

        yunnan = {}
        yunnan["pos"] = {"x": 974, "y": 781}
        yunnan["name"] = "云南省"

        names = ["昆明市"]

        startpos = [888, 738]
        colum_abs_dis = 70
        row_abs_dis = 40
        citys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis, max_col=4)
        yunnan["citys"] = citys

        for city in citys:
            if city["name"] == "昆明市":
                names = ['东川区', '寻甸回族彝族自治县', '五华区', '西山区', '宜良县', '石林彝族自治县', '呈贡区', '晋宁区',
                         '安宁市', '富民县', '禄劝彝族苗族自治县', '官渡区', '盘龙区', '嵩明县']
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis, max_col=4,
                                            skips={0: 2, 5: 2, 10: 2})
                city["countys"] = contys
                # self.judgePos(contys)
        provices.append(yunnan)

        #
        sichuan = {}
        sichuan["pos"] = {"x": 1106, "y": 737}
        sichuan["name"] = "四川省"

        names = ["成都市"]

        startpos = [961, 576]
        colum_abs_dis = 70
        row_abs_dis = 40
        citys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis, max_col=4)
        sichuan["citys"] = citys

        for city in citys:
            if city["name"] == "成都市":
                names = ['郫县', '高新区', '高新西区', '彭州市', '都江堰市', '大邑县', '蒲江县', '青白江区', '简阳市', '崇州市',
                         '金堂县', '邛崃市', '新津区', '温江区', '郫都区', '双流区', '武侯区', '金牛区', '新都区', '龙泉驿区',
                         '成华区', '青羊区', '锦江区']
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis, max_col=4,
                                            skips={})
                city["countys"] = contys
                # self.judgePos(contys)
        provices.append(sichuan)

        jiangsu = {}
        jiangsu["pos"] = {"x": 1097, "y": 616}
        jiangsu["name"] = "江苏省"

        names = ['连云港市', '宿迁市', '南京市', '南通市', '淮安市', '扬州市', '泰州市', '盐城市', '镇江市', '苏州市', '无锡市', '常州市', '徐州市']

        startpos = [888, 738]
        colum_abs_dis = 70
        row_abs_dis = 40
        citys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis, max_col=4)
        jiangsu["citys"] = citys

        for city in citys:
            if city["name"] == "连云港市":
                names = ['新浦区', '东海县', '连云区', '灌云县', '灌南县', '赣榆区', '海州区']
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis, max_col=4,
                                            )
                city["countys"] = contys
                # self.judgePos(contys)
            if city["name"] == "宿迁市":
                names = ['沭阳县', '泗阳县', '泗洪县', '宿豫区', '宿城区']
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis, max_col=4,
                                            )
                city["countys"] = contys
                # self.judgePos(contys)
            if city["name"] == "南京市":
                names = ['白下区', '下关区', '浦口区', '雨花台区', '江宁区', '溧水区', '六合区', '高淳区', '建邺区', '鼓楼区', '秦淮区', '栖霞区', '玄武区']
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis, max_col=4,
                                            )
                city["countys"] = contys
                # self.judgePos(contys)
            if city["name"] == "南通市":
                names = ['经济技术开发区', '如皋市', '海门市', '海安市', '如东县', '启东市', '港闸区', '通州区', '崇川区']
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis, max_col=4,
                                            skips={0: 2}
                                            )
                city["countys"] = contys
                # self.judgePos(contys)
            if city["name"] == "淮安市":
                names = ['清河区', '楚州区', '清浦区', '淮阴区', '盱眙县', '金湖县', '洪泽区', '涟水县', '清江浦区', '淮安区']
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis, max_col=4,
                                            )
                city["countys"] = contys
            if city["name"] == "扬州市":
                names = ['维扬区', '经济开发区', '邗江区', '广陵区', '仪征市', '高邮市', '宝应县', '江都区']
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis, max_col=4,
                                            skips={1: 2})
                city["countys"] = contys
            if city["name"] == "泰州市":
                names = ['靖江市', '泰兴市', '兴化市', '姜堰区', '高港区', '海陵区']
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis, max_col=4,
                                            )
                city["countys"] = contys
            if city["name"] == "盐城市":
                names = ['阜宁县', '滨海县', '射阳县', '建湖县', '亭湖区', '盐都区', '东台市', '大丰区', '响水县']
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis, max_col=4,
                                            )
                city["countys"] = contys
            if city["name"] == "镇江市":
                names = ['新区', '扬中市', '润州区', '丹徒区', '京口区', '丹阳市', '句容市']
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis, max_col=4,
                                            )
                city["countys"] = contys
            if city["name"] == "苏州市":
                names = ['沧浪区', '平江县', '金阊区', '高新区', '张家港市', '虎丘区', '太仓市', '姑苏区', '吴江区', '相城区', '苏州工业园区', '常熟市', '吴中区',
                         '昆山市']
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis, max_col=4,
                                            skips={10: 2}
                                            )
                city["countys"] = contys
                # self.judgePos(contys)

            if city["name"] == "无锡市":
                names = ['崇安区', '南长区', '北塘区', '新区', '梁溪区', '新吴区', '江阴市', '滨湖区', '宜兴市', '锡山区', '惠山区']
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis, max_col=4,
                                            )
                city["countys"] = contys

            if city["name"] == "常州市":
                names = ['戚墅堰区', '金坛区', '溧阳市', '新北区', '武进区', '钟楼区', '天宁区']
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis, max_col=4,
                                            )
                city["countys"] = contys
                # self.judgePos(contys)

            if city["name"] == "徐州市":
                names = ['九里区', '新沂市', '泉山区', '铜山区', '云龙区', '睢宁县', '邳州市', '沛县', '丰县', '贾汪区', '鼓楼区']
                startpos = [885, 580]
                contys = self.gen_names_pos(names, startpos=startpos, x_dis=colum_abs_dis, y_dis=row_abs_dis, max_col=4,
                                            )
                city["countys"] = contys

        provices.append(jiangsu)

        return provices

    def gen_names_pos(self, names, startpos, x_dis, y_dis, max_col=4, skips={}):
        results = []
        num = 0
        for i, name in enumerate(names):
            result = {}
            result["name"] = name

            result["pos"] = {"x": startpos[0] + (num % max_col) * x_dis, "y": startpos[1] + int(num / max_col) * y_dis}
            results.append(result)
            if i in skips.keys():
                num += skips[i]
            else:
                num += 1
        return results

    def judgePos(self, results):
        for result in results:
            print(result["name"])
            self.moveTo(result["pos"])
            time.sleep(1)

    def moveTo(self, pos):
        pyautogui.moveTo(pos["x"], pos["y"], duration=0.25)

    def click(self):
        pyautogui.click(button="left")

    def moveAndClick(self, pos):
        addrecords()
        self.moveTo(pos)
        addrecords()
        self.click()
        addrecords()

    def set_pause(self, pause):
        pyautogui.PAUSE = pause

    def recordPosSamples(self, num, sleep=3):
        '''获取记录到的坐标点:param'''
        poslist = []
        for i in range(num):
            time.sleep(sleep)
            x, y = pyautogui.position()
            print("[{},{}]".format(x, y))
            poslist.append([x, y])
            s = pyautogui.confirm('请移动到下个坐标点')
            if s == "OK":
                pass

            return poslist
        return poslist

    def printNowPos(self):
        sleep = 3
        time.sleep(sleep)
        x, y = pyautogui.position()
        print("[{},{}]".format(x, y))

    def flashData(self, data_path, use_status=True):
        '''刷数据:param'''

        try:
            data = pd.read_pickle(data_path)
        except:
            data = pd.read_csv(data_path)
        data = data.reset_index()
        print("过滤之前", data.index)
        print(data.index)

        print(data.shape)
        error_num = 0
        if use_status and not use_sqllite:
            status_path = "./data/status.csv"

            if os.path.exists(status_path):
                try:
                    status_data = pd.read_csv(status_path)
                except Exception as e:
                    print("{}".format(e))
                    status_data = pd.DataFrame(data, columns=["cityname", "楼盘", "区", "户型图"])
                    status_data["导入状态"] = 0
                status_data.drop_duplicates("户型图", "last", inplace=True)
                status_data.to_csv(status_path, index=False)
                data = pd.merge(data, status_data, how="left", on="户型图", suffixes=("", "_y"))
            else:
                status_data = pd.DataFrame(data, columns=["cityname", "楼盘", "区", "户型图"])
                status_data["导入状态"] = 0
                data = pd.merge(data, status_data, how="left", on="户型图", suffixes=("", "_y"))
                sub_data = data.iloc[:, ["cityname", "楼盘", "区", "户型图"]]
                sub_data.to_csv(status_path, index=False)

        if use_status and not use_sqllite:
            data_use = data[~data.导入状态.astype(str).str.contains("OK")]
        elif not use_sqllite:
            data_use = data
        else:
            boollist = []
            for dati in tqdm(data.index):
                print(dati)

                dat = data.iloc[dati]
                cursor.execute("select * from status where imgurl = ?", (dat["户型图"],))
                values = cursor.fetchall()
                print("find", values)
                if len(values) < 1:
                    print("insert")
                    cursor.execute("insert into status (cityname,loupan,contyname,imgurl,status) values (?,?,?,?,?)",
                                   (dat["cityname"], dat["楼盘"], dat["区"], dat["户型图"], 0))

                    boollist.append(True)
                else:
                    print("select")
                    val = values[0]
                    stat = val[-1]
                    print("状态{}".format(stat))
                    if int(stat) == 0:
                        pass
                        boollist.append(True)
                    elif int(stat) == 1:
                        boollist.append(False)
                        continue
                    else:
                        boollist.append(True)
            print(len(boollist))

            print("过滤之前:{}".format(data.shape))
            conn.commit()
            data_use = data[boollist]
            print("过滤之后:{}".format(data_use.shape))
            data_use = data_use.reset_index(drop=True)
            time.sleep(10)

        print(data_use.index)
        for dati in tqdm(data_use.index):
            print(dati)

            dat = data_use.iloc[dati]
            # print(dat)
            try:
                if len(dat["图片编码"]) > 10 and dat["community_name"] != "UNKNOW":
                    image = base64_to_image(dat["图片编码"])
                    cv2.imwrite("./cache/test.jpg", image)

                    dat["house_name"] = "{}户型库-".format(dat["城市"]) + dat["house_name"]
                    path = os.path.join(os.getcwd(), "cache/test.jpg")
                    print(path)
                    result = self.actionCreateNewHouse(dat)
                    while result == "RESTART":
                        cleanrecords(imgs)
                        self.restartDr()
                        result = self.actionCreateNewHouse(dat)
                    if result == "OK":

                        result1 = self.actionImportImage(imgpath=path, name="./results/" + dat["house_name"] + ".png")
                    else:
                        self.restartDr()
                        continue

                    while result1 == "RESTART":
                        cleanrecords(imgs)
                        self.restartDr()
                        result = self.actionCreateNewHouse(dat)
                        result1 = self.actionImportImage(imgpath=path,
                                                         name="./results/" + dat["house_name"] + "./results/" + dat[
                                                             "house_name"] + ".png")
                    if result1 == "OK":
                        pass
                    else:
                        self.restartDr()
                        continue

                else:
                    print("异常数据跳过")
                    if len(dat["图片编码"]) < 10:
                        result = "ImageError"
                    else:
                        result = "LocError"
                    error_num += 1
                print("状态更新")
                if use_status and not use_sqllite:
                    with open(status_path, "a+", encoding="utf-8") as f:
                        f.write("{},{},{},{},{}\n".format(dat["cityname"], dat["楼盘"], dat["区"], dat["户型图"], result))

                    data_use.iloc[dati]["导入状态"] = result
                elif use_sqllite:
                    if "Error" in result:

                        cursor.execute("update  status set status = ? where imgurl = ?",
                                       (-1, dat["户型图"]))
                        conn.commit()
                    else:
                        cursor.execute("update  status set status = ? where imgurl = ?",
                                       (1, dat["户型图"]))
                        conn.commit()
            except  Exception as e:
                print(e)
                #raise (e)
                continue

        print("总数据{}，异常:{}".format(len(data.index), error_num))
        if use_status and not use_sqllite:
            status_data = pd.read_csv(status_path)
            status_data.drop_duplicates("户型图", "last", inplace=True)
            status_data.to_csv(status_path, index=False)
        if use_sqllite:
            conn.close()
        pyautogui.confirm("处理完成:总数据{}，异常:{}".format(len(data_use.index), error_num))


def addrecords():
    if record:
        r_n = np.array(pyautogui.screenshot())
        imgs.append(r_n)


def cleanrecords(t):
    print("清理钱imgs的长度:{}".format(len(imgs)))
    imgs.clear()
    print("清理后的imgs的长度:{}".format(len(imgs)))


def imgs2mp4(imgs, filename, fps=3):
    print("imgs {}".format(len(imgs)))
    filename_ = filename + ".mp4"
    shape = [480*4, 270*4]
    imgs_ = []

    with imageio.get_writer(filename_, fps=fps) as video:
        for i, img in enumerate(imgs):
            img_data = np.array(img, dtype=np.uint8)
            img_data = Image.fromarray(img_data)
            img_data = img_data.resize(shape)
            img_data = np.array(img_data)
            # img_data = np.resize(img_data, shape)
            imgs_.append(img_data)
            video.append_data(img_data)
    #filename_ = filename + ".gif"
    #imageio.mimsave(filename_, imgs_, fps=fps)
    print("save path:{}".format(filename_))
    return filename_


if __name__ == "__main__":
    try:
        path = r"D:\work\dr_client_sit_20201102103026_Release_20201030_2.11.9\sit_20201102103026_Release_20201030_2.11.9\DramaticReality.exe"
        p = path
        s = pyautogui.prompt("请输入DR exe的文件位置:默认值为:{}如果不修改默认值请随便输入一个字符点击确定".format(path))

        if len(s) > 5:
            p = s

        s = pyautogui.confirm('请确认是否需要记录整个过程')
        addrecords()
        if s == "OK":
            record = True
            r_n = np.array(pyautogui.screenshot())
            imgs.append(r_n)
            addrecords()
        else:
            cleanrecords(imgs)
            record = False

        worker = Upload2DR(0.5, DR_PATH=p)
        worker.normWindowsPath("D:/workspace\\200")
        worker.printNowPos()
        worker.getHouseLocDict()

        # 测试启动 Dr软件
        ########################################
        worker.startAndLoggin()
        time.sleep(15)
        worker.clickHouseLib()
        print("star dr sucess")

        worker.printNowPos()
        # print("关闭DR软件")
        # worker.shutdownDr()
        ########################################

        ########################################
        # 批量刷入户型图
        # worker.flashData("./data/test.pkl")
        worker.flashData("./data/test_union.csv")
        ########################################
    except Exception as e:
        print(e)
        import traceback

        print(traceback.format_exc())
        s = input()

    ########################################
    # 测试 新建户型并且 输入户型信息
    # worker = Upload2DR(0.8)
    # data = {}
    # data["house_name"] = "十几家庄"
    # data["county_name"] = "栖霞区"
    # data["community_name"] = "陆家嘴小区"
    # path = os.path.join(os.path.dirname(__file__), "cache/test.jpg")
    # print(path)
    #
    # worker.actionCreateNewHouse(data)
    # worker.actionImportImage(imgpath=path)

    #############################################
    # pos = {"x":425,"y":143}
    # worker.moveAndClick(pos)
    # worker.writeWords("翠屏城小区")

    worker.printNowPos()
    ###############################################
    # 测试文本输入
    # pos = worker.getHouseCommunityNameLoc()
    # worker.moveAndClick(pos)
    # time.sleep(1)
    # worker.writeWords("翠屏城小区")
    #
    ###############################################

    ########################################
    # # 测试区县坐标点的位置是否正确
    # poses = worker.getHouseCountyLocs()
    # for name,pos in poses.items():
    #     print(name)
    #     worker.moveTo(pos)
    #     time.sleep(3)
    #########################################
