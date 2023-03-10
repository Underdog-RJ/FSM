#  Copyright (c) 2021 European Union
#  *
#  Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
#  European Commission – subsequent versions of the EUPL (the "Licence");
#  You may not use this work except in compliance with the Licence.
#  You may obtain a copy of the Licence at:
#  *
#  https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
#  *
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the Licence is distributed on an "AS IS" basis,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the Licence for the specific language governing permissions and limitations
#  under the Licence.
#
#
from MyLogger import logger
import os
import random
import time

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from utility import real_time_cal
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time

'''
Mandatory parameters:
1. select type of analysis: 'one_case', 'comparison', 'post_processing'
2. select scenario: 'cut_in', 'cut_out', 'car_following'
'''

'''
Optional parameters:
* 'model'           = 'FSM' (model to be used for 'one_case' of TTC cut_in post_processing. 
                            Models = 'FSM' 'RSS', 'Reg157', 'CC_human_driver')
* 'initial_speed'   = 50 (speed in km/h for 'one_case' analysis: 'car_following', 'cut_out', cut_in')
* 'deceleration'    = 9.81 * 0.5 (deceleration in m/s^2 for 'one_case' analysis: 'car_following')
* 'obstacle_speed'  = 20 (speed in km/h for 'one_case' analysis: 'cut_in')
* 'lateral_speed'   = -1. (speed in m/s for 'one_case' analysis: 'cut_in', 'cut_out')
* 'front_distance'  = 50 (distance in m for 'one_case' analysis: 'cut_in', 'cut_out')
* 'save_image'      = False (boolean True/False for storing/discarding images, 'post_processing' only)
'''

# analyses = ['one_case', 'comparison', 'post_processing']
# analysis = analyses[0]
analysis = 'one_case'

scenarios = ['cut_in', 'cut_out', 'car_following']
scenario = scenarios[0]

# models = ['FSM', 'RSS', 'Reg157', 'CC_human_driver']
# model = models[0]
model = 'FSM'


def getRandom():
    ego_speed = random.randint(40, 60)
    diff = random.randint(5, 9)
    obj_speed = ego_speed - diff
    ego_pos = random.randint(30, 50)
    obj_pos = random.randint(120, 160)
    dis = random.randint(10, 20)
    time = random.uniform(2, 4)
    res = {}
    res["ego_longitudeSpeed"] = ego_speed
    res["ego_startPositionS"] = ego_pos
    res["obj_longitudeSpeed"] = obj_speed
    res["obj_startPositionS"] = obj_pos
    res["Distance_ds_triggerValue"] = dis
    res["laneChangeDuration"] = time
    return res


def getNormal(x1, x2, low, high, decimal=0):
    while True:
        res = round(np.random.normal(x1, np.sqrt(x2), 1)[0], decimal)
        if res >= low and res <= high:
            break
    return res


def getFromParameterSpace():
    ego_speed = getNormal(55.87, 25, 40, 70, 0)
    obj_speed = getNormal(60, 27, 40, 70, 0)
    while ego_speed <= obj_speed:
        ego_speed = getNormal(55.87, 25, 40, 70, 0)
        obj_speed = getNormal(60, 27, 40, 70, 0)

    ego_pos = 50
    obj_pos = 150
    dis = getNormal(30, 5, 20, 40, 0)
    time = getNormal(2.2, 1, 1, 6, 2)
    res = {}
    res["ego_longitudeSpeed"] = ego_speed
    res["ego_startPositionS"] = ego_pos
    res["obj_longitudeSpeed"] = obj_speed
    res["obj_startPositionS"] = obj_pos
    res["Distance_ds_triggerValue"] = dis
    res["laneChangeDuration"] = time
    return res


def getFromParameterSpace1():
    ego_speed = getNormal(55.87, 25, 40, 70, 0)
    obj_speed = getNormal(45.93, 26.62, 40, 70, 0)
    while ego_speed <= obj_speed:
        ego_speed = getNormal(55.87, 25, 40, 70, 0)
        obj_speed = getNormal(45.93, 26.62, 40, 70, 0)

    ego_pos = 30
    obj_pos = 60
    # dis = getNormal(34.58, 18.55, 20, 40, 0)
    dis = getNormal(15, 36, 5, 20, 0)
    time = getNormal(2.2, 1, 1, 6, 2)
    res = {}
    res["ego_longitudeSpeed"] = ego_speed
    res["ego_startPositionS"] = ego_pos
    res["obj_longitudeSpeed"] = obj_speed
    res["obj_startPositionS"] = obj_pos
    res["Distance_ds_triggerValue"] = dis
    res["laneChangeDuration"] = time
    return res


def getNextIndex():
    f = open('./index1.txt', encoding='utf-8')
    line = f.readlines()[-1].strip()  # 读取第一行
    f.close()
    next_index = str(int(line) + 1)
    f = open('./index1.txt', 'a+', encoding='utf-8')
    f.writelines('\n' + next_index)
    f.close()
    return next_index


def drawDistribution(obj_list, obj_path):
    plt.figure(figsize=(20, 10), dpi=100)
    plt.hist(np.array(obj_list), 200)
    plt.savefig(obj_path)


def getObj(ego_speed, obj_speed, dis, time):
    res = {}
    res["ego_longitudeSpeed"] = ego_speed
    res["ego_startPositionS"] = 50
    res["obj_longitudeSpeed"] = obj_speed
    res["obj_startPositionS"] = 150
    res["Distance_ds_triggerValue"] = dis
    res["laneChangeDuration"] = time
    return res


def KMeans():
    o1 = getObj(59, 47, 17, 1.95)
    o2 = getObj(58, 41, 6, 3.88)
    o3 = getObj(58, 50, 18, 2.15)
    t = []
    t.append(o1)
    t.append(o2)
    t.append(o3)
    return t


def multiRun():
    # 创建一个包含2条线程的线程池
    with ThreadPoolExecutor(max_workers=4) as pool:
        future1 = pool.submit(action)
        future2 = pool.submit(action)
        future3 = pool.submit(action)
        future4 = pool.submit(action)

        future1.add_done_callback(get_result)
        future2.add_done_callback(get_result)
        future3.add_done_callback(get_result)
        future4.add_done_callback(get_result)

        pool.shutdown(wait=True)


import redis

re = redis.Redis(host='159.27.184.52', port=9763, password="Zhangzhengxu123.")


# 定义一个准备作为线程任务的函数
def action():
    res_list = []
    for i in range(0, 50):
        res = getFromParameterSpace1()
        res_dic = real_time_cal.run_one_case(scenario, res)
        res.update(res_dic)
        res_list.append(res)

    return res_list


def get_result(future):
    logger.info("record result")
    print(len(future.result()))


# with ThreadPoolExecutor(max_workers=4) as pool:
#     future1 = pool.submit(action)
#     future2 = pool.submit(action)
#     future3 = pool.submit(action)
#     future4 = pool.submit(action)
# startTime = time.time()
# while future1.done() and future2.done() and future3.done() and future4.done():
#     logger.error("future1:" + str(len(future1.result())))
#     logger.error("future2:" + str(len(future2.result())))
#     logger.error("future3:" + str(len(future3.result())))
#     logger.error("future4:" + str(len(future4.result())))
#     logger.error("zhixignjieshu ")
#     endTime = time.time()
#     logger.error("diff" + str(endTime - startTime))
#     break
if __name__ == '__main__':
    next_index = getNextIndex()
    dir_name = "./res"
    dir_name = os.path.join(dir_name, next_index)
    if os.path.exists(dir_name) is False:
        os.mkdir(dir_name, 777)

    # 获取随机参数
    res_list = []
    ego_speeds = []
    obj_speeds = []
    distance_list = []
    duration_list = []

    startTime = time.time()

    # multiRun()

    executor = ThreadPoolExecutor(max_workers=4)
    all_task = [executor.submit(action) for i in range(0, 4)]

    for future in as_completed(all_task):
        data = future.result()
        for d in data:
            logger.info(d)
        res_list.append(data)

    # 参数分布
    # ego_speeds.append(res["ego_longitudeSpeed"])
    # obj_speeds.append(res["obj_longitudeSpeed"])
    # distance_list.append(res["Distance_ds_triggerValue"])
    # duration_list.append(res["laneChangeDuration"])

    # 生成结果csv
    pd_list = pd.DataFrame(res_list)
    csv_path = os.path.join(dir_name, "res.csv")
    pd_list.to_csv(csv_path)
    endTime = time.time()
    diff = endTime - startTime
    logger.info("diff:" + str(diff))

    # # 生成ego_speed_dis
    # ego_speed_dis = os.path.join(dir_name, "ego_speed_dis.png")
    # drawDistribution(ego_speeds, ego_speed_dis)
    #
    # # 生成obj_speed_dis
    # obj_speed_dis = os.path.join(dir_name, "obj_speed_dis.png")
    # drawDistribution(obj_speeds, obj_speed_dis)
    #
    # # 生成laneChangeDuration
    # distance_ds_triggerValue_dis_path = os.path.join(dir_name, "distance_ds_triggerValue_dis.png")
    # drawDistribution(distance_list, distance_ds_triggerValue_dis_path)
    #
    # # 生成laneChangeDuration
    # laneChange_duration_dis_path = os.path.join(dir_name, "laneChange_duration_dis.png")
    # drawDistribution(duration_list, laneChange_duration_dis_path)


