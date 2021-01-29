#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/11/6 15:42
# @Author  : zhuzhaowen
# @email   : shaowen5011@gmail.com
# @File    : auto_upload_img_2_dr.py
# @Software: PyCharm
# @desc    : "通过界面操作的方式批量导入双十一户型图到DR软件中"

import pyautogui
import pyperclip

pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = True
import numpy as np
from PIL import Image
import time
import os
import pandas as pd
from util.util import base64_to_image
import pickle
import cv2
from tqdm import tqdm


class Upload2DR():
    def __init__(self, pause):
        self.pause = pause
        self.set_pause(pause)

    def actionCreateNewHouse(self, data):
        ''':param创建新户型的动作'''

        house_name = data.get("house_name")
        county_name = data.get("county_name")
        community_name = data.get("community_name")
        print("户型名:{} 区县:{} 小区名称:{}".format(house_name, county_name, community_name))
        pos = self.getCreateHousePos()
        self.moveAndClick(pos)
        time.sleep(10)
        pos = self.getHouseInputNamePos()
        self.moveAndClick(pos)
        self.writeWords(house_name)  # ("117平米户型")
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

        # pos = self.getHouseAuthPubSetLoc()
        # self.moveAndClick(pos)

        pos = self.getConfirmButtonLoc()
        self.moveAndClick(pos)
        return "OK"

    def actionImportImage(self, imgpath):
        # pos = self.getSelectFilePathLoc()
        # self.moveAndClick(pos)
        # pyautogui.press("tab", presses=5, interval=0.2)
        # pyautogui.press('enter')
        # pyautogui.press('delete')
        dirname = os.path.dirname(imgpath)
        print("dirname{}".format(dirname))

        self.writeWords(self.normWindowsPath(imgpath))
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

        self.moveAndClick(pos)
        time.sleep(10)

        pos = self.getHouseSaveButtonLoc()
        self.moveAndClick(pos)
        time.sleep(5)

        pos = self.getGoUperButtonLoc()
        self.moveAndClick(pos)
        pos = self.getConfirmExitButtonLoc()
        self.moveAndClick(pos)
        time.sleep(1)

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
        self.moveTo(pos)

        self.click()

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
        s = pyautogui.confirm("请确认已打开DR软件 并且 DR软件的 界面右上方有新建户型 按钮,确认将继续，取消将退出")
        if s == "OK":
            pass
        else:
            exit()

        data = pd.read_pickle(data_path)
        data["cityname"] = "南京市"
        data["区"] = "白下区"
        data["county_name"] = "白下区"
        data["county_name"] = "白下区"
        data["community_name"] = "双11户型图"
        # start = 170 + 20 + 3 + 8 + 146
        # s = pyautogui.confirm("请确认是否需要重置开始数据？当前位置为{}".format(start))
        # if s == "OK":
        #     start = pyautogui.prompt('请输入从第几条(int)数据开始，当前为:{}'.format(170 + 20 + 3 + 8 + 146))
        #     start = int(start)

        #data = data[data.楼盘.str.contains("建业")]
        print(data.shape)
        error_num = 0
        if use_status:
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

        if use_status:
            data_use = data[~data.导入状态.astype(str).str.contains("OK")]
        else:
            data_use = data

        for dati in tqdm(data_use.index):
            dat = data_use.iloc[dati]
            # print(dat)
            if len(dat["图片编码"]) > 10 :
                if dat["community_name"] == "UNKNOW":
                    dat["community_name"] = "双11测试户型"
                    dat["cityname"] = "南京市"

                image = base64_to_image(dat["图片编码"])
                cv2.imwrite("./cache/test.jpg", image)

                dat["house_name"] = "{}".format(  dat["house_name"])
                path = os.path.join(os.getcwd(), "cache/test.jpg")
                print(path)
                result = self.actionCreateNewHouse(dat)
                self.actionImportImage(imgpath=path)
            else:
                print("异常数据跳过")
                if len(dat["图片编码"]) < 10:
                    result = "ImageError"
                else:
                    result = "LocError"
                error_num += 1
            print("状态更新")
            if use_status:
                with open(status_path, "a+", encoding="utf-8") as f:
                    f.write("{},{},{},{},{}\n".format(dat["cityname"], dat["楼盘"], dat["区"], dat["户型图"], result))

                data_use.iloc[dati]["导入状态"] = result

        print("总数据{}，异常:{}".format(len(data.index), error_num))
        if use_status:
            status_data = pd.read_csv(status_path)
            status_data.drop_duplicates("户型图", "last", inplace=True)
            status_data.to_csv(status_path, index=False)
        pyautogui.confirm("处理完成:总数据{}，异常:{}".format(len(data_use.index), error_num))


if __name__ == "__main__":

    worker = Upload2DR(0.5)
    worker.normWindowsPath("D:/workspace\\200")
    worker.getHouseLocDict()

    ########################################
    # 批量刷入户型图
    # worker.flashData("./data/test.pkl")
    worker.flashData("./data/test_1111.pkl")
    ########################################

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
