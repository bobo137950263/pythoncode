#!/usr/bin/env python
#-*- coding:utf-8 -*-
def paixu(list):
    left_list = []
    middle_list = []
    right_list = []
    if len(list)>=2:
        temp_middle = list[0]
        middle_list.append(temp_middle)
        for temp_data in list[1:]:
            if temp_data > temp_middle:
                right_list.append(temp_data)
            elif temp_data == temp_middle:
                middle_list.append(temp_data)
            else:
                left_list.append(temp_data)
        return paixu(left_list) + middle_list + paixu(right_list)
        # return paixu(left_list), middle_list, paixu(right_list)
    else:
        return list

list1=[1,-1,0,5,3,10,6,20,11,0,1,99,23,100,5]
print(paixu(list1))