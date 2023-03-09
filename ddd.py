from concurrent.futures import ThreadPoolExecutor
import threading
import time


# 定义一个准备作为线程任务的函数
def action(max):
    my_sum = 0
    for i in range(max):
        print(threading.current_thread().name + '  ' + str(i))
        my_sum += i
    return my_sum


def get_result(future):
    print(future.result())


# 创建一个包含2条线程的线程池
with ThreadPoolExecutor(max_workers=4) as pool:
    # 向线程池提交一个task, 50会作为action()函数的参数
    future1 = pool.submit(action, 50)
    # 向线程池再提交一个task, 100会作为action()函数的参数
    future2 = pool.submit(action, 100)
    future3 = pool.submit(action, 200)
    future4 = pool.submit(action, 300)

    # 为future1添加线程完成的回调函数
    future1.add_done_callback(get_result)
    print('--------------')
    # 为future2添加线程完成的回调函数
    future2.add_done_callback(get_result)
    future3.add_done_callback(get_result)
    future4.add_done_callback(get_result)