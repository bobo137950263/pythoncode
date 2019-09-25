# 生成2-100的自然数
list1 = [x for x in range(2,100)]
# print(list1)
# 定义一个方法，排除
n = list1[0]
def division(x):
    if x % n > 0:
        return True
    else:
        return False

# 定义一个空列表，用来存放素数
list2 = []

for x in range(10):
    # print(n)
    list2.append(n)
    list1 = list(filter(division,list1))
    n = list1[0]

print(list2)

