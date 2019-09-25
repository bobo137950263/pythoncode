#!/usr/bin/env python
#-*- coding:utf-8 -*-
def odd(n):
    if n % 2 == 0:
        return True
    else:
        return False

g = (x for x in range(10))

# fil = filter(odd,g)
# print(fil,type(fil))
# print(next(fil))

def _odd_iter():
    n = 1
    while True:
        n = n + 2
        yield n

oddobj = _odd_iter()
print(oddobj,type(oddobj))
for i in range(10):
    print(next(oddobj))