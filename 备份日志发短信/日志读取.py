#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os
file_path='E:\pythoncode\github_cloud\pythoncode\备份日志发短信'
os.chdir(file_path)
print(os.listdir(file_path))
file = open("日志",encoding='utf-8',mode='r')
data = file.readlines()
# print(data)
os.path.exists()

for temdata in data:
    if 'start_time' in temdata:
        start_time = temdata
    elif 'end_time' in temdata:
        end_time = temdata
    elif 'incremental' in temdata:
        incremental = temdata

string_format = '----------------' \
                'Instance Name:%s' \
                '%s%s%s'\
                %(temdata,start_time,end_time,incremental)
print(string_format)
