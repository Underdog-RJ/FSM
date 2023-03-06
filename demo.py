# coding=utf-8
import math
import os
import random
import time

import matplotlib.pyplot as plt
import pandas as pd
from xml.dom.minidom import parse
import xml.dom.minidom
import numpy as np


def getNextIdnex():
    f = open('./index.txt', encoding='utf-8')
    line = f.readlines()[-1].strip()  # 读取第一行
    f.close()
    next_index = int(line) + 1
    f = open('./index.txt', 'a+', encoding='utf-8')
    f.writelines('\n' + str(next_index))
    f.close()
    return next_index


wpipe_path1 = "/opt/module/heartPipe1"
wpipe_path2 = "/opt/module/heartPipe2"


def testWrite():
    wpipe1 = os.open(wpipe_path1, os.O_SYNC | os.O_CREAT | os.O_RDWR)
    wpipe2 = os.open(wpipe_path2, os.O_SYNC | os.O_CREAT | os.O_RDWR)
    heart_format = "time:{}-----------aiUnitId:{}-----------ip:{}-----------heart:{}".format(
        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 1, 1, 1)
    os.write(wpipe1, str.encode(heart_format))
    os.write(wpipe2, str.encode(heart_format))
    print(heart_format)


def test():
    for parent, dirnames, filenames in os.walk("./data/cut_in_34/live_dir"):
        for filename in filenames:
            print(filename)


def create_veh_from_csv():
    cnt_pd = pd.read_csv("./full_log.csv", header=6)
    for row_index, row in cnt_pd.iterrows():
        row[" #1 World_Position_Y [m] "]
        row[" #1 World_Position_X [m] "]
        row[" #1 Vel_X [m/s] "]
        row[" #1 Vel_Y [m/s] "]
        row[" #2 World_Position_Y [m] "]
        row[" #2 World_Position_X [m] "]
        row[" #2 Vel_X [m/s] "]
        row[" #2 Vel_Y [m/s] "]


from utility import global_parameters as gp

xoscPath = "/home/Rupeng119_com/esmini/resources/xosc/"


def createXOSC(name):
    ego_startPositionS = gp.ego_startPositionS
    ego_longitudeSpeed = gp.ego_longitudeSpeed / 3.6
    obj_startPositionS = gp.obj_startPositionS
    obj_longitudeSpeed = gp.obj_longitudeSpeed / 3.6
    laneChangeDuration = gp.laneChangeDuration
    Distance_ds_triggerValue = gp.Distance_ds_triggerValue
    # 创建xosc文件
    # 使用minidom解析器打开XML文档
    DOMTree = xml.dom.minidom.parse("./cut-in.xosc")
    Data = DOMTree.documentElement

    # 自车开始位置
    ego_position = Data.getElementsByTagName("Private")[0].getElementsByTagName("LanePosition")[0]
    ego_position.setAttribute("s", str(ego_startPositionS))
    ego_speed = Data.getElementsByTagName("Private")[0].getElementsByTagName("AbsoluteTargetSpeed")[0]
    ego_speed.setAttribute("value", str(ego_longitudeSpeed))
    ego_speed_1 = Data.getElementsByTagName("Maneuver")[0].getElementsByTagName("AbsoluteTargetSpeed")[0]
    ego_speed_1.setAttribute("value", str(ego_longitudeSpeed))

    # obj
    obj_position = Data.getElementsByTagName("Private")[1].getElementsByTagName("LanePosition")[0]
    obj_position.setAttribute("s", str(obj_startPositionS))
    obj_speed = Data.getElementsByTagName("Private")[1].getElementsByTagName("AbsoluteTargetSpeed")[0]
    obj_speed.setAttribute("value", str(obj_longitudeSpeed))
    ego_speed_1 = Data.getElementsByTagName("Maneuver")[1].getElementsByTagName("AbsoluteTargetSpeed")[0]
    ego_speed_1.setAttribute("value", str(ego_longitudeSpeed))

    # duration
    LaneChangeActionDynamics = Data.getElementsByTagName("LaneChangeActionDynamics")[0]
    LaneChangeActionDynamics.setAttribute("value", str(laneChangeDuration))

    # RelativeDistanceCondition
    RelativeDistanceCondition = Data.getElementsByTagName("RelativeDistanceCondition")[0]
    RelativeDistanceCondition.setAttribute("value", str(Distance_ds_triggerValue))
    cnt_path = os.path.join(xoscPath, name)
    fp = open(cnt_path, 'w', encoding='utf-8')
    DOMTree.writexml(fp, indent='', addindent='', newl='', encoding='utf-8')

    fp.close()
    return cnt_path


def remoteCall(xoscPath, savePath):
    execCommand = "esmini --osc {} --fixed_timestep 0.1 --csv_logger {} --collision".format(xoscPath, savePath)
    os.system(execCommand)


def getRandom():
    ego_speed = random.randint(40, 60)
    diff = random.randint(0, 10)
    obj_speed = ego_speed - diff
    ego_pos = random.randint(30, 50)
    obj_pos = random.randint(120, 160)
    dis = random.randint(10, 20)
    time = random.uniform(2, 5)
    res = {}
    res["ego_longitudeSpeed"] = ego_speed
    res["ego_startPositionS"] = ego_pos
    res["obj_longitudeSpeed"] = obj_speed
    res["obj_startPositionS"] = obj_pos
    res["Distance_ds_triggerValue"] = dis
    res["laneChangeDuration"] = time
    return res


def getNormal(x1, x2, low, high):
    while True:
        res = round(np.random.normal(x1, np.sqrt(x2), 1)[0], 2)
        if res >= low and res <= high:
            break
    return res


def getFromParameterSpace():
    ego_speed = getNormal(55.87, 25, 40, 70)
    obj_speed = getNormal(60, 27, 40, 70)
    while ego_speed <= obj_speed:
        ego_speed = getNormal(55.87, 25, 40, 70)
        obj_speed = getNormal(60, 27, 40, 70)
    flag = False
    if ego_speed > obj_speed:
        flag = True

    ego_pos = 50
    obj_pos = 150
    dis = getNormal(30, 5, 20, 40)
    time = getNormal(2.2, 1, 1, 6)
    res = {}
    res["ego_longitudeSpeed"] = ego_speed
    res["ego_startPositionS"] = ego_pos
    res["obj_longitudeSpeed"] = obj_speed
    res["obj_startPositionS"] = obj_pos
    res["Distance_ds_triggerValue"] = dis
    res["laneChangeDuration"] = time
    return res, flag


def plotDistribution():
    res = np.random.normal(55.87, np.sqrt(25), 2000)
    plt.figure(figsize=(20, 10), dpi=100)
    plt.hist(res, 200)
    plt.savefig("./dis.png")
    # plt.show()


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
    o1 = getObj(55.2357, 46.7839, 33.6304, 2.43757)
    o2 = getObj(53.7136, 48.1925, 33.1925, 2.4607)
    o3 = getObj(59.2418, 44.3714, 33.7363, 2.41332)
    t = []
    t.append(o1)
    t.append(o2)
    t.append(o3)
    return t


if __name__ == '__main__':
    # name = {'name': 'Gage'}
    # age = {'age': 25}
    # name.update(age)
    print(math.ceil(float("4.11") * 10))
    # ego_speed = getNormal(55.87, 25, 40, 70)
    # print(ego_speed)
    # plotDistribution()

    # # 获取随机参数
    # count = 0
    # for i in range(0, 100):
    #     _, flag = getFromParameterSpace()
    #     if flag:
    #         count += 1
    # print(count)
    # res_list = []
    # for i in range(0, 100):
    #     res = getRandom()
    #     print(res["ego_longitudeSpeed"])
