#!/usr/bin/env python
#-*- coding:utf-8 -*-

def _odd_iter():
    n = 1
    while True:
        n = n + 2
        yield n

def _not_divisible(n):
    return lambda x : x % n > 0

def primes():
    '''
    实际上是利用生成的奇数生成器，先拿第一个奇数3去做整除，找出所有余数不为0的，组成一个生成器。然后获取该生成器的下一个，应该是5，改生成器的所有数整除5，把5打印出来，因为5本来就是素数，5整除所有前面的数，都有余数。
    :return:
    '''
    yield 2
    it = _odd_iter()
    while True:
        n = next(it)
        yield n
        it = filter(_not_divisible(n),it)

# print(primes())
for n in primes():
    if n < 100:
        print(n)
    else:
        break
