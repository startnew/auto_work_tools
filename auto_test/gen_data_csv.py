#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/11/9 14:19
# @Author  : zhuzhaowen
# @email   : shaowen5011@gmail.com
# @File    : gen_data_csv.py
# @Software: PyCharm
# @desc    : "获取导入的信息并筛选"

import pandas as pd
import urllib
import pypinyin
import time
from util.util import base64_to_image, image_to_base64, exc_time
import numpy as np
import cv2
from auto_search_address import get_key_words_adname


class dataProcess():
    def __init__(self):

        self.ad_name_map_dict = {}

    def processOriData(self, data_path, save_data="./data/test"):
        data = pd.read_excel(data_path)
        self.data = data
        print(self.data.shape)
        self.clean_data()
        self.data = self.data[:]

        print(self.data.shape)
        if self.data.shape[0] > 0:
            self.add_adname()
            self.add_img_info()
            self.save_data(save_data)

    def processOriDatas(self, data_paths, save_data="./data/test_union", has_cache=False):
        datas = []
        for data_path in data_paths:
            try:
                print(data_path)
                data = pd.read_excel(data_path)
                print(data.columns[0], data.shape[1])
                if int(data.shape[1]) == 14 and data.columns[0] != "城市":
                    data = pd.read_excel(data_path, header=None, names= \
                        ["城市", "楼盘", "类型", "单价", "总价", "项目地址", "最新开盘", "全部图片url", "户型",
                         "户型图", "居室", "建面", "均价",
                         "状态"])
                    print(data.head())
                elif int(data.shape[1]) == 5 and data.columns[0] == "house_id":
                    data = pd.read_excel(data_path)
                    data["楼盘"] = "威尼斯水城"
                    data["name"] = data["house_id"].map(lambda x: "house_id_{}".format(x))
                    data["城市"] = "南京市"
                    data["类型"] = "住宅"
                    data["项目地址"] = "威尼斯水城"
                    data["居室"] = data["structure_name"]
                    data["建面"] = data["area"]
                    data["户型"] =data["house_id"].map(lambda x: "house_id_{}".format(x))





                self.data = data
                print(self.data.shape)
                self.clean_data()
                if self.data.shape[0]<1:
                    continue
                # self.data = self.data[:]

                print(self.data.shape)
                self.add_adname()
                self.add_img_info()
                datas.append(self.data)
            except  Exception as e:
                print("ERROR {}".format(e))
                continue
        union_pd = pd.concat(datas)
        self.data = union_pd
        self.clean_data()
        print("合并后的尺寸大小", union_pd.shape)
        # 去重后的尺寸大小
        print(len(union_pd.户型图.unique()))
        union_pd.drop_duplicates("户型图", "first", inplace=True)
        self.data = union_pd
        print("去重后尺寸大小", union_pd.shape)
        limit = False
        downImg = False
        if limit:
            name = "建业"
            data_junfa = self.data[self.data.楼盘.str.contains(name)]

            print("junfa的户型数据", )
        # print(data_建业.head())
            self.data["junfa与否"] = self.data.楼盘.str.contains(name)


            self.data = data_junfa

        if has_cache and os.path.exists(save_data+".pkl"):
            print("使用cache")

            cache_data = pd.read_pickle(save_data + ".pkl")

            self.add_adname(cache=cache_data)
            if downImg:self.add_img_info(cache=cache_data)
        else:
            self.add_adname()
            if downImg:self.add_img_info()
        # self.data = self.data[self.data.cityname.str.contains("成都")]
        #print("{}的个数:{}".format(name, self.data.shape))
        print(self.data.shape)

        self.save_data(save_data)

    def save_data(self, path):
        self.data.to_excel(path + ".xlsx")
        self.data.to_csv(path + ".csv")
        self.data.to_pickle(path + ".pkl")

    @exc_time
    def clean_data(self):
        self.data = self.data[self.data["户型图"].notna()]
        self.data = self.data[self.data["楼盘"].notna()]
        self.data = self.data[self.data["项目地址"].notna()]
        self.data = self.data[self.data["户型"].notna()]

    @exc_time
    def add_adname(self,cache=None):
        self.data["区"] = self.data.apply(lambda x: self.map_adname(x["楼盘"], x["城市"],cache), axis=1)
        self.data["cityname"] = self.data.apply(lambda x: self.map_cityname(x["楼盘"], x["城市"],cache), axis=1)
        self.data["pname"] = self.data.apply(lambda x: self.map_pname(x["楼盘"], x["城市"],cache), axis=1)
        self.data["location"] = self.data.apply(lambda x: self.map_location(x["楼盘"], x["城市"], cache), axis=1)


    def map_adname(self, x, city,cache=None):
        k = str(x) + str(city)

        if cache is not None:
            try:
                select_df = cache[(cache.楼盘.str.contains(x)) & (cache.城市.str.contains(city))]
                # print(select_df.shape)
                if select_df.shape[0] > 0:
                    if "区" in select_df.columns:
                        if len(select_df["区"].values[0]) != 0:
                            # print(select_df["图片编码"].values[0])
                            print("SUCCESS from cache file  LOCPOS{}".format(type(select_df["区"].values[0])))

                            return select_df["区"].values[0]
                        else:
                            print("cache中指定字段值为空 使用url获取并编码")
                    else:
                        print("cache中没有指定字段 使用api数据")
                else:
                    print("没有找到url符合的 使用api数据")
            except Exception as e:

                print("Error {}:x{} city:{} ".format(e, x, city))
                #raise e

        if k in self.ad_name_map_dict.keys():
            return self.ad_name_map_dict.get(k).get("adname")
        else:
            r = get_key_words_adname(x, city=city)
            self.ad_name_map_dict[k] = r
            return r.get("adname")

    def map_pname(self, x, city,cache=None):
        k = str(x) + str(city)
        if cache is not None:
            try:
                select_df = cache[(cache.楼盘.str.contains(x)) & (cache.城市.str.contains(city))]
                # print(select_df.shape)
                if select_df.shape[0] > 0:
                    if "pname" in select_df.columns:
                        if len(select_df["pname"].values[0]) != 0:

                            print("SUCCESS from cache file LOCPOS {}".format(type(select_df["pname"].values[0])))

                            return select_df["pname"].values[0]
                        else:
                            print("cache中指定字段值为空 使用url获取并编码")
                    else:
                        print("cache中没有指定字段 使用api数据")
                else:
                    print("没有找到url符合的 使用api数据")
            except  Exception as e:
                print("Error {}:x{} city:{} ".format(e,x,city))

        if k in self.ad_name_map_dict.keys():
            return self.ad_name_map_dict.get(k).get("pname")
        else:
            r = get_key_words_adname(x, city=city)
            self.ad_name_map_dict[k] = r
            return r.get("pname")

    def map_location(self, x, city, cache):
        k = str(x) + str(city)
        if cache is not None:
            try:
                select_df = cache[(cache.楼盘.str.contains(x)) & (cache.城市.str.contains(city))]
                # print(select_df.shape)
                if select_df.shape[0] > 0:
                    if "location" in select_df.columns:
                        if len(select_df["location"].values[0]) != 0:

                            print("SUCCESS from cache file LOCPOS {}".format(type(select_df["pname"].values[0])))

                            return select_df["location"].values[0]
                        else:
                            print("cache中指定字段值为空 使用url获取并编码")
                    else:
                        print("cache中没有指定字段 使用api数据")
                else:
                    print("没有找到url符合的 使用api数据")
            except  Exception as e:
                print("Error {}:x{} city:{} ".format(e, x, city))

        if k in self.ad_name_map_dict.keys():
            return self.ad_name_map_dict.get(k).get("location")
        else:
            r = get_key_words_adname(x, city=city)
            self.ad_name_map_dict[k] = r
            return r.get("location")

    def map_cityname(self, x, city,cache):
        k = str(x) + str(city)
        if cache is not None:
            try:
                select_df = cache[cache.楼盘.str.contains(x) & cache.城市.str.contains(city)]
                # print(select_df.shape)
                if select_df.shape[0] > 0:
                    if "cityname" in select_df.columns:
                        if len(select_df["cityname"].values[0]) != 0:

                            print("SUCCESS from cache file {} LOCPOS".format(type(select_df["cityname"].values[0])))

                            return select_df["cityname"].values[0]
                        else:
                            print("cache中指定字段值为空 使用url获取并编码")
                    else:
                        print("cache中没有指定字段 使用api数据")
                else:
                    print("没有找到url符合的 使用api数据")
            except Exception as e:
                print("ERROR {}".format(e))
        if k in self.ad_name_map_dict.keys():
            return self.ad_name_map_dict.get(k).get("cityname")
        else:
            r = get_key_words_adname(x, city=city)
            self.ad_name_map_dict[k] = r
            return r.get("cityname")
    @exc_time
    def add_img_info(self, cache=None):
        self.data["图片编码"] = self.data.户型图.map(lambda x: self.down_and_encode(x,cache))

        def gen_name(x, y, z):
            try:
                return str(x) + str(y) + str(z)
            except:
                return str(x)

        self.data["house_name"] = self.data.apply(lambda x: gen_name(x["户型"], x["类型"], x["居室"]), axis=1)
        self.data["county_name"] = self.data["区"]
        self.data["community_name"] = self.data["楼盘"]
        if "全部图片url" in self.data.columns:
            self.data = self.data.drop(["全部图片url"], axis=1)

    def down_and_encode(self, imgurl,cache_data):
        #print(imgurl)

        num = 0
        try:
            if cache_data is not None:
                select_df = cache_data[cache_data.户型图.str.contains(imgurl)]
                #print(select_df.shape)
                if select_df.shape[0]>0:
                    if "图片编码" in select_df.columns:
                        if len(select_df["图片编码"].values[0]) != 0:
                            #print(select_df["图片编码"].values[0])
                            print("SUCCESS from cache file {}".format(type(select_df["图片编码"].values[0])))

                            return select_df["图片编码"].values[0]
                        else:
                            print("cache中指定字段值为空 使用url下载并编码")
                    else:
                        print("cache中没有指定字段 使用下载数据")
                else:
                    print("没有找到url符合的 使用下载数据")
            print(imgurl)
            r = self.down_load_url(imgurl)
            r = self.encodeImg(r)
            print("SUCCESS")
        except Exception as e:
            # raise  e
            print("ERROR {}".format(e))
            r = ''
        if r == '' and "original" not in imgurl:
            return self.down_and_encode(imgurl+"!original",cache_data)
        return r

    def down_load_url(self, imageUrl):
        resp = urllib.request.urlopen(imageUrl)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")

        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return image

    def encodeImg(self, image):
        return image_to_base64(image)

    def decodeImg(self, str64):
        return base64_to_image(str64)


if __name__ == "__main__":
    dp = dataProcess()
    import os

    dir_name = r"D:\workspace\2020\标准户型库"
    paths = []
    for root, dirs, files in os.walk(dir_name):
        for name in files:
            if name.endswith(".xlsx") or name.endswith(".xls"):
                k = os.path.join(root, name)
                # if "河南" in k:
                paths.append(k)

    print(paths)
    # dp.processOriData(r"D:\workspace\2020\标准户型库\南京\贝壳找房-南京-2020-11-06-house.xlsx.xlsx")
    dp.processOriDatas(paths,save_data="./data/test_union",has_cache=True)
    #dp.processOriDatas(paths, save_data="./data/test_jianye", has_cache=False)
    print(dp.data.head())
    print(dp.data.columns)
