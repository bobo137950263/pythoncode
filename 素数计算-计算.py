list1 = (x for x in range(2, 100))
n = next(list1)


def division(x):
    if x % n > 0:
        return True
    else:
        return False


list2 = []

for x in range(10):
    # print(n)
    list2.append(n)
    list1 = filter(division, list1)
    n = next(list1)


    def division(x):
        if x % n > 0:
            return True
        else:
            return False

print(list2)