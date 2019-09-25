#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''判断数字是否为阿姆斯特朗数字'''
def amsterang(number):
    string = str(number)
    length = len(string)
    total_sum = 0
    count = 0
    for i in string:
        temp = int(i)
        total_sum +=temp**(length)
    if number == total_sum:
        print(total_sum)

for x in range(1000):
    amsterang(x)

