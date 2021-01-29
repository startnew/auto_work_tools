#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/11/11 11:14
# @Author  : zhuzhaowen
# @email   : shaowen5011@gmail.com
# @File    : code_generator.py
# @Software: PyCharm
# @desc    : "代码生成器 自动生成全国 省市 区县的 代码"

import pymysql

user = "root"
passwd = "aijia1234567"
host = "mysql-01.db.sit.ihomefnt.org"
db_name = "htp_config"

db = pymysql.connect(host=host,port=3306,user=user,passwd=passwd,db=db_name )

cursor = db.cursor()

try:
    #r = cursor.execute("SELECT * FROM `t_areas` where level = 1 order by area_id;")
    r = cursor.execute('SELECT area_name FROM `t_areas` where level = 1 order by area_id;')
    data = cursor.fetchall()
    provience = [x[0] for x in data]
    strs = ''' 
            provices = []
            provices_names = {0}
    
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
                    city["countys"] = contys'''.format(provience)
    print(strs)
except Exception as e:
    print(e)
    pass
db.close()
