#!/usr/bin/env python
#-*- coding:utf-8 -*-

# def Step():
#     print("step 1")
#     yield 1
#     print("step 2")
#     yield 3
#     print("step 3")
#     yield 5

# a = Step()
# print(next(a))
# print(next(a))
# print(next(a))
# print(next(a))
# print(next(a))

def Triangle(n):
    '''杨辉三角'''
    if n == 1:
        list = [1]
    elif n == 2:
        list = [1,1]
    else:
        temp = n -2
        x = 1
        list = [1,1]
        templist = Triangle(n - 1)
        while x <= temp:
            list.insert(x,templist[x]+templist[x-1])
            x += 1
    # print(list)
    return list

def PrintTriangle(n):
    tem = 1
    while tem <= n:
        print(Triangle(tem))
        tem += 1


# PrintTriangle(10)


'''将输入的名字，规则化输出'''
def StringFormat(string):
    string = str(string)
    return string.lower().title()
L1 = ['adam', 'LISA', 'barT']
L2 = map(StringFormat,L1)
# print(list(L2))

'''求一个列表的乘积'''
L3 = [1,3,5,7,9]
# print(sum(L3))
from functools import reduce
def Multiple(x,y):
    result = x * y
    return result
Result = reduce(Multiple,L3)
# print(Result)

def Mul(x,y):
    return x * 10 + y
def Div(x,y):
    return x /10 + y
def String2List(string):
    dict = {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '0': 0}
    string = str(string)
    return dict[string]

def String2Float(string):
    string = str(string)
    if '.' in string:
        '''如果字符串中有小数点，拆分两段，一段用于乘法，一段用于除法'''
        list1_str = string.split(".")[0]
        list2_str = string.split(".")[1]
        list2_str=reversed(list2_str)
    else:
        list1_str = string
        list2_str = '0'
    list1_int = list(map(String2List,list1_str))
    list2_int = list(map(String2List,list2_str))
    zhengshu = reduce(Mul,list1_int)
    xiaoshu = reduce(Div,list2_int)
    return zhengshu + xiaoshu /10

print(String2Float('123.456'),type(String2Float('123.456')))
# print(String2Float('123.456'),type(String2Float('123.456')))
print(String2Float('2345'),type(String2Float('2345')))

