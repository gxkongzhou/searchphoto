# _*_ coding:utf-8 _*_

import math
from copy import deepcopy

def grouping(li, num):
    """
    :param li: 需要分页的列表
    :param num: 每一页页码数量
    :return: 分页后列表
    需要导入math模块
    """
    handleli = deepcopy(li)
    zu = math.ceil(len(handleli)/num)
    new_list = []
    n = 0
    while True:
        if n == (zu - 1):
            new_list.append(handleli[::])
            break
        page = handleli[0:num]
        del handleli[0:(num)]
        new_list.append(page)
        n += 1
    return new_list