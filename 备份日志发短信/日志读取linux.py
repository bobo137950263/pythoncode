#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os
import sendsms as sendsms

#file_path='E:\pythoncode\github_cloud\pythoncode\备份日志发短信'
#file_path='/usr/local/mysql/mysqldata/databak/today/2019-07-09/data1'
file_path='/usr/local/mysql/mysqldata/databak/today'
os.chdir(file_path)
today_path=file_path + '/'+ os.listdir(file_path)[0]
os.chdir(today_path)
message=''
for datadir in ['data1','data2','data3']:
    os.chdir(today_path)
    temdatadir=today_path + '/'+datadir
    if os.path.exists(temdatadir):
        os.chdir(temdatadir)
        file = open("xtrabackup_info",mode='r')
        data = file.readlines()


        for temdata in data:
            if 'start_time' in temdata:
                start_time = temdata
            elif 'end_time' in temdata:
                end_time = temdata
            elif 'incremental' in temdata:
                incremental = temdata.splitlines()

        #string_format = '%s%s%s'%(start_time,end_time,incremental)
        string_format = '----------------\n' \
                    'Instance Name:%s\n' \
                        'Backup done!\n' \
                    '%s%s%s'\
                    %(datadir,start_time,end_time,incremental)
    else:
        string_format = '----------------\n' \
                        'Instance Name:%s\n' \
                        'Backup Missing!\n' \
                        % (datadir)

    message +=string_format
        #print(string_format)
#print(message)
PhoneNumber='18710159600'
sendsms.sendsms(PhoneNumber,message)