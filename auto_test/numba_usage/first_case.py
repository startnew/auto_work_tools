#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/9/25 15:12
# @Author  : zhuzhaowen
# @email   : shaowen5011@gmail.com
# @File    : first_case.py
# @Software: PyCharm
# @desc    : "numba hello word"

from numba import jit
from numba import int32
from numba import cuda
import time
import random



def calc_time(func):
    def new_func(*args, **args2):
        t0 = time.time()
        back = func(*args, **args2)
        print("**** {} taken for {}".format(time.time() - t0, func.__name__))


        return back
    return new_func

@calc_time
@jit(nopython=True)
def mote_carlo_pi(nsamples):
    acc = 0
    for i in range(nsamples):
        x = random.random()
        y = random.random()
        if (x**2 + y**2) < 1.0:
            acc += 1
    return 4.0 * acc / nsamples

@calc_time
def mote_carlo_pi_ori(nsamples):
    acc = 0
    for i in range(nsamples):
        x = random.random()
        y = random.random()
        if (x**2 + y**2) < 1.0:
            acc += 1
    return 4.0 * acc / nsamples

@calc_time
@cuda.jit
def increment_by_one(an_array):
    # Thread id in a 1D block
    tx = cuda.threadIdx.x
    # Block id in a 1D grid
    ty = cuda.blockIdx.x
    # Block width, i.e. number of threads per block
    bw = cuda.blockDim.x
    # Compute flattened index inside the array
    pos = tx + ty * bw
    if pos < an_array.size:
        an_array[pos] += 1


@calc_time
@jit(int32(int32, int32))
def f_l(x,y):
    return x + y

@calc_time
@jit
def f(x,y):
    return x + y




if __name__ == "__main__":

    # 对比后当数量级超过百万时，numba 加速明显超过原生 状态，其余时候 小于原生速度
    num = 10000000
    mote_carlo_pi(num)
    mote_carlo_pi_ori(num)

    import numpy as np
    s = np.zeros([num])

    increment_by_one(s)
    print(s)

    print(f(3,4))
    print(f(1j,2))
    print(f_l(3,4))