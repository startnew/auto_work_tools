#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/5/10 12:47
# @Author  : zhaowen.zhu
# @Site    :
# @File    : MultiThread.py
# @Software: Python Idle
# @UpdateTime : 2022/05/07
import threading
import time
import multiprocessing
from multiprocessing import Pool
import platform


def exc_time(func):
    def new_func(*args, **args2):
        st = time.perf_counter()

        back = func(*args, **args2)
        end = time.perf_counter()
        print("@ 函数:{} 用时: {} s".format(func.__name__, end - st))
        return back

    return new_func


class MyTMultithread(threading.Thread):
    '''
    自定义的线程函数,
    功能:使用多线程运行函数,函数的参数只有一个file,并且未实现结果值的返回
    args:
        filelist   函数的参数为列表格式，
        funname    函数的名字为字符串，函数仅有一个参数为file
        delay      每个线程之间的延迟，
        max_threads 线程的最大值
    '''

    def __init__(self, filelist, delay, funname, max_threads=50):
        threading.Thread.__init__(self)
        self.funname = funname
        self.filelist = filelist[:]
        self.delay = delay
        self.max_threads = max_threads

    @exc_time
    def startrun(self):
        self.results = [0] * len(self.filelist)
        ori_filelist = self.filelist[:]

        def runs():

            time.sleep(self.delay)

            while True:
                try:
                    file = self.filelist.pop()

                except IndexError as e:
                    break
                else:
                    index = ori_filelist.index(file)
                    # 保持顺序
                    self.results[index] = self.funname(file)

        threads = []
        while threads or self.filelist:
            for thread in threads:
                if not thread.is_alive():
                    threads.remove(thread)
                thread.join()
            while len(threads) < self.max_threads and self.filelist:
                thread = threading.Thread(target=runs)
                thread.setDaemon(True)
                thread.start()
                # print("线程开启", len(threads))
                threads.append(thread)

    @staticmethod
    def static_startrun(filelist, delay, funname, max_threads=50):
        results = [0] * len(filelist)
        ori_filelist = filelist[:]

        def runs():

            time.sleep(delay)

            while True:
                try:
                    file = filelist.pop()
                except IndexError as e:
                    break
                else:
                    index = ori_filelist.index(file)
                    # 保持顺序
                    results[index] = funname(file)

        threads = []
        while threads or filelist:
            for thread in threads:
                if not thread.is_alive():
                    threads.remove(thread)
                thread.join()
            while len(threads) < max_threads and filelist:
                thread = threading.Thread(target=runs)
                thread.setDaemon(True)
                thread.start()

                threads.append(thread)
        return results

    def get_result(self):
        try:
            return self.results
        except Exception:
            return None

    def startAndGet(self, start=True):
        if start:
            self.startrun()
            result = self.get_result()
            # print("start and get result", result)
            return result
        else:
            return None


class Mymultiprocessing(MyTMultithread):
    '''
    多进程运行函数，多进程多线程运行函数


    args:
        filelist   函数的参数为列表格式，
        funname    函数的名字为字符串，函数仅有一个参数为file
        delay      每个线程\进程之间的延迟，
        max_threads 最大的线程数
        max_multiprocess 最大的进程数

    '''

    def __init__(
            self,
            filelist,
            delay,
            funname,
            max_multiprocess=1,
            max_threads=1):

        self.funname = funname
        self.filelist = filelist[:]
        self.delay = delay
        self.max_threads = max_threads
        self.max_multiprocess = max_multiprocess
        self.num_cpus = multiprocessing.cpu_count()
        print(self.funname, self.num_cpus)

    @exc_time
    def multiprocessingOnly(self):
        '''
    只使用多进程
        '''
        num_process = min(self.num_cpus, self.max_multiprocess)
        processes = []
        while processes or self.filelist:
            for p in processes:
                if not p.is_alive():
                    # print(p.pid,p.name,len(self.filelist))
                    processes.remove(p)
            while len(processes) < num_process and self.filelist:
                try:
                    file = self.filelist.pop()
                    time.sleep(self.delay)
                except IndexError as e:
                    break
                else:
                    p = multiprocessing.Process(
                        target=self.funname, args=(file,))
                    p.start()
                    processes.append(p)

    @exc_time
    def multiprocessingOnlyUsePool(self):
        '''
    使用进程池方式
        '''
        p = Pool(min(self.max_multiprocess, self.num_cpus))

        while self.filelist:
            try:
                file = self.filelist.pop()

                time.sleep(self.delay)

            except IndexError as e:
                break
            else:
                p.apply_async(self.funname, (file,))
        p.close()
        p.join()

    @exc_time
    def multiprocessingWithReturn(self):
        '''
        只使用 多进程 并且 获取返回结果，需要在main下面运行,jupyter notebook 运行会报错
        :return:
        '''
        results = [0] * len(self.filelist)
        index_all = len(results)
        p = Pool(min(self.max_multiprocess, self.num_cpus))
        i = 0

        while self.filelist:
            try:
                file = self.filelist.pop()
                i += 1
                index = index_all - i
                time.sleep(self.delay)

            except IndexError as e:
                break
            else:
                results[index] = p.apply_async(self.funname, (file,))
        p.close()
        p.join()
        return [x.get() for x in results]

    @exc_time
    def multiprocessingWithReturn_(self):
        '''
        只使用 多进程 并且 获取返回结果
        :return:
        '''
        results = [0] * len(self.filelist)
        index_all = len(results)

        p = Pool(min(self.max_multiprocess, self.num_cpus))
        num_process = min(self.num_cpus, self.max_multiprocess)
        processes = []
        i = 0
        while processes or self.filelist:
            for p in processes:
                if not p.is_alive():
                    # print(p.pid,p.name,len(self.filelist))
                    processes.remove(p)
            while len(processes) < num_process and self.filelist:
                try:
                    file = self.filelist.pop()
                    i += 1
                    index = index_all - i
                    time.sleep(self.delay)

                except IndexError as e:
                    break
                else:
                    print(file)
                    results[index] = p.map(self.funname, (file,))
                    # results.append(result)
                    # p.start()
                    # processes.append(p)

        return [x.get() for x in results]

    @exc_time
    def multiprocessingThreads(self):
        '''多进程+多线程'''
        num_process = min(self.num_cpus, self.max_multiprocess)
        DATALISTS = []
        tempmod = len(self.filelist) % (num_process)
        CD = int((len(self.filelist) + 1 + tempmod) / (num_process))
        for i in range(num_process):
            if i == num_process - 1:
                DATALISTS.append(self.filelist[i * CD:-1])
            else:
                DATALISTS.append(self.filelist[(i * CD):((i + 1) * CD)])

        try:
            processes = []
            for i in range(num_process):

                MultThread = MyTMultithread(
                    DATALISTS[i], self.delay, self.funname, self.max_threads)

                if platform.system() != "Linux":
                    p = multiprocessing.Process(
                        target=MultThread.static_startrun, args=(
                            DATALISTS[i], self.delay, self.funname, self.max_threads))
                else:
                    # windows 使用下面的语句会报错 can't pickle _thread.lock objects
                    p = multiprocessing.Process(target=MultThread.startrun)

                processes.append(p)

            for p in processes:
                # print('wait join ')
                p.start()
            for p in processes:
                # print('p join ')
                p.join()

            # print('waite over')
        except Exception as e:
            print('error :', e)
        print('end process')

    @exc_time
    def multiprocessingThreadsWithReturn(self):
        # 顺序保持
        p = Pool(min(self.max_multiprocess, self.num_cpus))
        num_process = min(self.num_cpus, self.max_multiprocess)

        DATALISTS = []
        tempmod = len(self.filelist) % (num_process)
        CD = int((len(self.filelist) + 1 + tempmod) / (num_process))
        for i in range(num_process):
            if i == num_process:
                DATALISTS.append(self.filelist[i * CD:-1])
            DATALISTS.append(self.filelist[(i * CD):((i + 1) * CD)])
        results = [0] * num_process
        st = time.time()
        MultThreads = []
        for i in range(num_process):
            MultThread = MyTMultithread(
                DATALISTS[i], self.delay, self.funname, self.max_threads)
            MultThreads.append(MultThread)
            results[i] = p.apply_async(
                MultThread.static_startrun,
                (DATALISTS[i],
                 self.delay,
                 self.funname,
                 self.max_threads))

        p.close()
        p.join()
        results_ = []
        for result in results:
            infos = result.get()
            for info in infos:
                results_.append(info)
        return results_


def func1(file):
    import time
    for i in range(10):
        time.sleep(0.002)
    # print(file)
    return file


if __name__ == '__main__':
    a = list(range(0, 1000))
    NUM_P = 5  # 进程数
    NUM_T = 5  # 线程数
    delay = 0
    N = 10  # 打印前N个结果
    conclude_strs = ""

    st = time.perf_counter()
    for i_a in a:
        func1(i_a)
    end = time.perf_counter()

    print('*' * 50)
    strs_1 = '单进程使用时间:{}'.format(end - st)
    print(strs_1)
    conclude_strs += strs_1 + "\n"
    ori_speed_time = end - st
    '''
    测试使用5线程
    '''
    # perf_counter()会包含sleep()休眠时间
    st = time.perf_counter()
    asc = MyTMultithread(a, delay, func1, NUM_T)
    asc.startrun()
    end = time.perf_counter()
    print('*' * 50)
    strs_1 = '{}个线程使用时间{},节省{}% '.format(
        NUM_T, end - st, (ori_speed_time - (end - st)) / ori_speed_time * 100)
    print(strs_1)
    conclude_strs += strs_1 + "\n"
    # 测试使用5个进程
    st = time.perf_counter()
    asd = Mymultiprocessing(a, delay, func1, NUM_P)
    asd.multiprocessingOnly()
    end = time.perf_counter()
    print('*' * 50)
    strs_1 = '{}个进程使用时间{},节省{}% '.format(
        NUM_P, end - st, (ori_speed_time - (end - st)) / ori_speed_time * 100)
    print(strs_1)
    conclude_strs += strs_1 + "\n"

    # 测试使用进程池的结果
    st = time.perf_counter()
    asd = Mymultiprocessing(a, delay, func1, NUM_P)
    asd.multiprocessingOnlyUsePool()
    end = time.perf_counter()
    print('*' * 50)
    strs_1 = '{}个进程（进程池方式）使用时间{},节省{}% '.format(
        NUM_P, end - st, (ori_speed_time - (end - st)) / ori_speed_time * 100)
    print(strs_1)

    conclude_strs += strs_1 + "\n"

    # 测试使用5进程5线程
    st = time.perf_counter()
    multiPT = Mymultiprocessing(a, delay, func1, NUM_P, NUM_T)
    multiPT.multiprocessingThreads()
    end = time.perf_counter()
    print('*' * 50)
    strs_1 = '{}个进程 {}个线程 使用时间{},节省{}% '.format(
        NUM_P, NUM_T, end - st, (ori_speed_time - (end - st)) / ori_speed_time * 100)
    print(strs_1)
    conclude_strs += strs_1 + "\n"

    '''
    测试使用5线程 带返回
    '''
    st = time.perf_counter()
    asc = MyTMultithread(a, delay, func1, NUM_T)
    results = asc.startAndGet()
    print(results[:N])
    end = time.perf_counter()
    print('*' * 50)
    strs_1 = '{}个线程带返回使用时间{},节省{}% '.format(
        NUM_T, end - st, (ori_speed_time - (end - st)) / ori_speed_time * 100)
    print(strs_1)
    conclude_strs += strs_1 + "\n"

    '''
      测试使用多进程 带返回
    '''
    st = time.perf_counter()
    multiPT = Mymultiprocessing(a, delay, func1, NUM_P)
    results = multiPT.multiprocessingWithReturn()
    end = time.perf_counter()
    print('*' * 50)
    print(results[:N])
    strs_1 = '{}个进程带返回使用时间{},节省{}% '.format(
        NUM_P, end - st, (ori_speed_time - (end - st)) / ori_speed_time * 100)
    print(strs_1)
    conclude_strs += strs_1 + "\n"

    # 多进程多线程带返回
    st = time.perf_counter()
    multiPT = Mymultiprocessing(a, delay, func1, NUM_P, NUM_T)
    print("start")
    results = multiPT.multiprocessingThreadsWithReturn()
    print(results[:N])
    end = time.perf_counter()
    print('*' * 50)
    print('多进程多线程带返回使用时间:', end - st)
    strs_1 = '{}个进程,每个进程{}个线程带返回使用时间{},节省{}% '.format(
        NUM_P, NUM_T, end - st, (ori_speed_time - (end - st)) / ori_speed_time * 100)
    print(strs_1)
    conclude_strs += strs_1 + "\n"

    print("总结:")
    print(conclude_strs)
