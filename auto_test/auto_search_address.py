#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/11/6 18:19
# @Author  : zhuzhaowen
# @email   : shaowen5011@gmail.com
# @File    : auto_search_address.py
# @Software: PyCharm
# @desc    : "自动查询地址 区域规划"

import urllib
import json
from pprint import pprint
import requests

#key = "97283aefa7bebe46dd478160cb0836ff"
key = "1efc7dccf80b6c5072577eab41ccd64d"
import random
import time


headers = {

"user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Mobile Safari/537.36"
}
def get_address_stand(address="南京"):
    '''行政区域查询:param'''
    url = "https://restapi.amap.com/v3/config/district?keywords={}&subdistrict=3&key={}".format(address, key)
    print(url)
    s = random.random()
    time.sleep(s)
    results = requests.request("GET", url,headers=headers)

    print(results.text)


def get_key_words_info(keywords="翠屏城", city="nanjing"):
    url = "https://restapi.amap.com/v3/place/text?keywords={}&city={}&output=json&offset=20&page=1&key={}&extensions=base".format(
        keywords, city, key)
    print(url)
    s = random.random()
    time.sleep(s)
    results = requests.request("GET", url,headers=headers)

    print(results.text)
    r = json.loads(results.text)
    pprint(r)

import random

def get_key_words_adname(keywords="", city="nanjing",back_k=''):
    url = "https://restapi.amap.com/v3/place/text?keywords={}&city={}&output=json&offset=20&page=1&key={}&extensions=base".format(
        keywords, city, key)
    s = random.random()
    time.sleep(s)



    results = requests.request("GET", url,headers=headers)
    print(url)
    k = {}
    k["pname"]="UNKNOW"
    k["city"] = "UNKNOW"
    k["cityname"]="UNKNOW"
    r = json.loads(results.text)
    print(r)
    if r:
        rs = r.get("pois", [])
        if len(rs)>0:

            r = {}
            r["pname"] = rs[0].get("pname")
            r["cityname"] = rs[0].get("cityname")
            r["adname"] = rs[0].get("adname")
            r["location"] = rs[0].get("location")
            print(r)

            return r
    if back_k:
        url2 = "https://restapi.amap.com/v3/place/text?keywords={}&city={}&output=json&offset=20&page=1&key={}&extensions=base".format(
            back_k, city, key)
        s = random.random()
        time.sleep(s)
        results = requests.request("GET", url2,headers=headers)
        r = json.loads(results.text)
        if r:
            rs = r.get("pois", [])
            if len(rs)>0:
                r = {}
                r["pname"] = rs[0].get("pname")
                r["cityname"] = rs[0].get("cityname")
                r["adname"] = rs[0].get("adname")
                r["location"] = rs[0].get("location")
                print(r)
                return r

    try:
        url2 = "https://restapi.amap.com/v3/place/text?keywords={}&city={}&output=json&offset=20&page=1&key={}&extensions=base".format(
            city, city, key)
        s = random.random()
        time.sleep(s)
        results = requests.request("GET", url2,headers=headers)
        r = json.loads(results.text)
        if r:
            rs = r.get("pois", [])
            r = {}
            r["pname"] = rs[0].get("pname")
            r["cityname"] = rs[0].get("cityname")
            r["adname"] = "UNKNOW"
            r["location"] = rs[0].get("location","UNKNOW")
            print(r)
            return r
    except:
        print(r)
        return k


    return k


if __name__ == "__main__":
    # get_address_stand("北京")
    #get_key_words_info()
    r = get_key_words_adname(keywords="翠屏城")
    print(r)

    r = get_key_words_adname(keywords="拉萨路")
    print(r)

    r = get_key_words_adname(keywords="钟山府")
    print(r)
    r = get_key_words_adname(keywords="远洋山水")
    print(r)

    r = get_key_words_adname(keywords="天润城")
    print(r)
    r = get_key_words_adname(keywords="金牛湖")
    print(r)

    r = get_key_words_adname(keywords="金轮翠雍华庭")
    print(r)

    r = get_key_words_adname(keywords="高淳雅园")
    print(r)

    r = get_key_words_adname(keywords="恍惚山",back_k="恍惚湖")
    print(r)



