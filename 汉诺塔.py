#!/usr/bin/env python
#-*- coding:utf-8 -*-

def MoveHannuo(n,A,B,C):
    source = A
    destination = C
    if n == 1:
        pass
        print("from %s to %s"%(source,destination))
    else:
        MoveHannuo(n-1,A,C,B)
        MoveHannuo(1,A,B,C)
        MoveHannuo(n-1,B,A,C)

A="A"
B="B"
C="C"
# MoveHannuo(1,A,B,C)
# MoveHannuo(2,A,B,C)
# MoveHannuo(3,A,B,C)
MoveHannuo(4,A,B,C)



