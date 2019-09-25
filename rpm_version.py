#!/usr/bin/env python
import os
import json
# dict_path="/tmp"
# rpm_dict_name='1111'
# rpm_path="/var/www/html/iso/Packages/"
# rpm_list_string = "ls " + rpm_path + "|grep .rpm"
# rpm_set = os.popen(rpm_list_string).readlines()
# rpm_dict = {}
#print(rpm_set)

#print(type(rpm_set),rpm_set)
# for rpm in rpm_set:
#     cmd_string = 'rpm -qp --qf "%{name} %{version}  %{release}   %{arch}" ' +rpm_path+ rpm
#     #print(cmd_string)
#     rpm_version_set = os.popen(cmd_string).readlines()[0]
#     #print(rpm_version_set)
#     rpm_version_list = rpm_version_set.split()
#     #print(rpm_version_list)
#     rpm_name = rpm_version_list[0]
#     rpm_version = rpm_version_list[1].split(".")
#     rpm_release = rpm_version_list[2].split(".")
#     rpm_arch = rpm_version_list[3]
#     rpm_dict[rpm_name]={'rpm_version':rpm_version,'rpm_release':rpm_release}
# print(rpm_dict)

# #dict_file = open('rpm_dict','w',encoding='utf-8')
# dict_file = open(rpm_dict_name,'w')
# string=json.dumps(rpm_dict)
# dict_file.write(string)
# dict_file.close()

from functools import reduce
def joint(string,item):
    string = string +"*"+item
    return string
version_list=["22", "7", "3"]
result = reduce(joint,version_list)
print(result)
list1=[]
list2=[]
str.isalpha()
list1.pop()
str.isdigit()