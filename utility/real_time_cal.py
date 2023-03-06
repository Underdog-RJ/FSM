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
import os

# import imageio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from post_processing import live_graph as li
from . import movement as mvt
from . import models as md
from . import global_parameters as gp

# init model
check = md.FSM_check_safety
react = md.FSM_react
dist = md.FSM_distance

length = gp.length
width = gp.width
iterations = gp.iterations
freq = gp.freq
deceleration = gp.g * 0.5

from xml.dom.minidom import parse
import xml.dom.minidom


def buildCnt(ego_veh, cut_in_veh, index, cfs, pfs):
    cnt = {}
    cnt["index"] = index
    cnt["ego_speed_profile_long"] = ego_veh.speed_profile_long[index]
    cnt["ego_speed_profile_lat"] = ego_veh.speed_profile_lat[index]
    cnt["ego_pos_profile_long"] = ego_veh.pos_profile_long[index]
    cnt["ego_pos_profile_lat"] = ego_veh.pos_profile_lat[index]
    cnt["cut_in_speed_profile_long"] = cut_in_veh.speed_profile_long[index]
    cnt["cnt_in_speed_profile_lat"] = cut_in_veh.speed_profile_lat[index]
    cnt["cnt_in_pos_profile_long"] = cut_in_veh.pos_profile_long[index]
    cnt["cnt_in_pos_profile_lat"] = cut_in_veh.pos_profile_lat[index]
    cnt["cfs"] = cfs
    cnt["pfs"] = pfs
    cnt["cfs_pfs"] = cfs + pfs

    return cnt


xoscPath = "/home/Rupeng119_com/esmini/resources/xosc/"


def createXOSC(name, save_path, res):
    ego_startPositionS = res["ego_startPositionS"]
    ego_longitudeSpeed = res["ego_longitudeSpeed"] / 3.6
    obj_startPositionS = res["obj_startPositionS"]
    obj_longitudeSpeed = res["obj_longitudeSpeed"] / 3.6
    laneChangeDuration = res["laneChangeDuration"]
    Distance_ds_triggerValue = res["Distance_ds_triggerValue"]
    # ego_startPositionS = gp.ego_startPositionS
    # ego_longitudeSpeed = gp.ego_longitudeSpeed / 3.6
    # obj_startPositionS = gp.obj_startPositionS
    # obj_longitudeSpeed = gp.obj_longitudeSpeed / 3.6
    # laneChangeDuration = gp.laneChangeDuration
    # Distance_ds_triggerValue = gp.Distance_ds_triggerValue

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
    ego_speed_1.setAttribute("value", str(obj_longitudeSpeed))

    # duration
    LaneChangeActionDynamics = Data.getElementsByTagName("LaneChangeActionDynamics")[0]
    LaneChangeActionDynamics.setAttribute("value", str(laneChangeDuration))

    # RelativeDistanceCondition
    RelativeDistanceCondition = Data.getElementsByTagName("RelativeDistanceCondition")[0]
    RelativeDistanceCondition.setAttribute("value", str(Distance_ds_triggerValue))
    cnt_path = os.path.join(xoscPath, name)
    fp = open(cnt_path, 'w', encoding='utf-8')
    DOMTree.writexml(fp, indent='', addindent='', newl='', encoding='utf-8')

    fp1 = open(save_path, 'w', encoding='utf-8')
    DOMTree.writexml(fp1, indent='', addindent='', newl='', encoding='utf-8')

    fp.close()
    return cnt_path


def remoteCall(xoscPath, savePath):
    execCommand = "esmini --osc {} --fixed_timestep 0.1 --csv_logger {} --collision".format(xoscPath, savePath)
    os.system(execCommand)


def getNextIndex():
    f = open('./index.txt', encoding='utf-8')
    line = f.readlines()[-1].strip()  # 读取第一行
    f.close()
    next_index = str(int(line) + 1)
    f = open('./index.txt', 'a+', encoding='utf-8')
    f.writelines('\n' + next_index)
    f.close()
    return next_index


# def makeGif(live_dir, dir_name, isCrash, last_index):
#     gif_list = []
#     print(last_index)
#     for i in range(1, last_index + 1):
#         image_path = str(i) + ".png"
#         gif_list.append(imageio.imread(os.path.join(live_dir, image_path)))
#     git_path = os.path.join(dir_name, str(isCrash) + ".gif")
#     imageio.mimwrite(git_path, gif_list, fps=3)


def cut_in(live_dir, csv_path, cnt_list, CFS, PFS, res):
    init_long_speed_ego = gp.initial_speed
    init_long_speed_c = gp.obstacle_speed
    lateral_speed = gp.lateral_speed
    long_dist = gp.front_distance

    init_long_speed_c = init_long_speed_c / 3.6
    init_long_speed_ego = init_long_speed_ego / 3.6

    init_pos_c = np.array([long_dist + length, 1.6 + width])
    init_pos_ego = np.array([0, 0])

    # cut_in_veh = mvt.create_profile_cutting_in(init_pos_c, init_long_speed_c, lateral_speed, iterations, freq)

    # ego_veh = mvt.create_profile_cutting_in(init_pos_ego, init_long_speed_ego, 0, iterations, freq)
    ego_veh, cut_in_veh, lengthTotal = mvt.create_veh_from_csv(csv_path)
    cut_in_veh.width = width
    cut_in_veh.length = length
    ego_veh.width = width
    ego_veh.length = length
    iterations = lengthTotal

    vehs = [ego_veh, cut_in_veh]

    count = 0
    max_cfs = 0
    start_pos_lat = 0.0
    crash_pos = -1

    for i in range(iterations - 1):
        diff = cut_in_veh.pos_profile_lat[i] - ego_veh.pos_profile_lat[i]
        if diff <= res["Distance_ds_triggerValue"]:
            start_pos_lat = ego_veh[i]

        cfs, pfs = mvt.control(ego_veh, cut_in_veh, freq, check, react, i)

        if cfs > 0.5 and cfs <= 1.0 and ego_veh.crash is False:
            count += 1
            max_cfs = max(max_cfs, cfs)
        # if cfs >= 1.0 and ego_veh.crash is False:
        #     count += 1
        #     max_cfs = max(max_cfs, cfs)
        if ego_veh.crash is False:
            last_index = i
        if ego_veh.crash is True and crash_pos == -1:
            crash_pos = ego_veh.pos_profile_lat

        # if ego_veh.crash == 1 and cfs > 0.5:
        #     count += 1
        #     max_cfs = max(max_cfs, cfs)
        #     last_index = i

        # build cnt info
        cnt = buildCnt(ego_veh, cut_in_veh, i, cfs, pfs)
        cnt_list.append(cnt)
        CFS.append(cfs)
        PFS.append(pfs)

        # li.plot_map(vehs, ax1, i, "cut_in", live_dir)

        # if ego_veh.crash == 1:
        # print("---")
        # fig.patch.set_facecolor((1, 0, 0, 0.2))
    end_pos_lat = start_pos_lat + res["Distance_ds_triggerValue"]
    if ego_veh.crash_type == 2 and crash_pos - end_pos_lat > 30:
        ego_veh.crash_type = 3
    res_dic = {}
    res_dic["last_index"] = last_index
    res_dic["count"] = count
    res_dic["max_cfs"] = max_cfs
    res_dic["crash_type"] = ego_veh.crash_type
    res_dic["start_pos_lat"] = start_pos_lat
    res_dic["end_pos_lat"] = end_pos_lat
    res_dic["crash_pos_lat"] = crash_pos

    return ego_veh, cut_in_veh, res


def car_following(live_dir):
    ur = gp.initial_speed
    imaginary_veh = mvt.create_profile_decel(np.array([42 + gp.length, 0]), 0, 10, 10, 10)

    initial_distance = md.FSM_distance(imaginary_veh, ur / 3.6)
    init_pos_c = np.array([initial_distance + gp.length, 0])
    init_pos_ego = np.array([0, 0])
    init_long_speed = ur / 3.6

    leader_veh = mvt.create_profile_decel(init_pos_c, deceleration, init_long_speed, iterations, freq)
    ego_veh = mvt.create_profile_decel(init_pos_ego, 0, init_long_speed, iterations, freq)

    leader_veh.width = gp.width
    leader_veh.length = gp.length
    ego_veh.width = gp.width
    ego_veh.length = gp.length

    vehs = [ego_veh, leader_veh]
    last_index = -1

    for i in range(iterations - 1):
        last_index = i
        if i == 1:
            plt.pause(2)

        cfs, pfs = mvt.control(ego_veh, leader_veh, freq, check, react, i)
        # build cnt info
        cnt = buildCnt(ego_veh, leader_veh, i, cfs, pfs)
        cnt_list.append(cnt)
        CFS.append(cfs)
        PFS.append(pfs)
        li.plot_map(vehs, ax1, i, "car_following", live_dir)
        if ego_veh.crash == 1:
            break
            fig.patch.set_facecolor((1, 0, 0, 0.2))
        if ego_veh.speed_profile_long[i] == 0:
            ego_veh.pos_profile_long[i:] = ego_veh.pos_profile_long[i]
            ego_veh.speed_profile_long[i:] = 0
            break
    return ego_veh, leader_veh, last_index


def cut_out(live_dir):
    ur = gp.initial_speed
    imaginary_veh = mvt.create_profile_decel(np.array([42 + gp.length, 0]), 0, 10, 10, 10)

    initial_distance = md.FSM_distance(imaginary_veh, ur / 3.6)
    init_pos_c = np.array([initial_distance + gp.length, 0])
    wandering_zone = gp.wandering_zone
    init_pos_ego = np.array([0, 0])
    init_long_speed = ur / 3.6
    dx0_f = gp.front_distance
    lateral_speed_cut_out = gp.lateral_speed

    initial_distance = dist(imaginary_veh, ur / 3.6)
    init_pos_c = np.array([initial_distance + length, 4])

    init_pos_st = np.array([init_pos_c[0] + dx0_f + length, 0])

    stopped_veh = mvt.create_profile_decel(init_pos_st, 0, 0, iterations, freq)
    cut_out_veh = mvt.create_profile_cutting_in(init_pos_c, init_long_speed, lateral_speed_cut_out, iterations, freq)
    cut_out_veh.pos_profile_lat = cut_out_veh.pos_profile_lat - 4
    ego_veh = mvt.create_profile_decel(init_pos_ego, 0, init_long_speed, iterations, freq)

    cut_out_veh.width = width
    cut_out_veh.length = length
    ego_veh.width = width
    ego_veh.length = length

    vehs = [ego_veh, cut_out_veh, stopped_veh]

    ego_veh.cfs, ego_veh.pfs = 0, 0
    last_index = -1

    for i in range(iterations - 1):
        CFS.append(ego_veh.cfs)
        PFS.append(ego_veh.pfs)
        last_index = i

        if abs(stopped_veh.pos_profile_lat[i] - cut_out_veh.pos_profile_lat[
            i]) - stopped_veh.width / 2 - cut_out_veh.width / 2 < 0 and abs(
            stopped_veh.pos_profile_long[i] - cut_out_veh.pos_profile_long[i]) - stopped_veh.length / 2 - \
                cut_out_veh.length / 2 < 0:
            cut_out_veh.crash = True
            cut_out_veh.speed_profile_long[i:] = 0
            cut_out_veh.speed_profile_lat[i:] = 0
            cut_out_veh.pos_profile_lat[i:] = cut_out_veh.pos_profile_lat[i]
            cut_out_veh.pos_profile_long[i:] = cut_out_veh.pos_profile_long[i]

        if cut_out_veh.crash:
            mvt.control(ego_veh, cut_out_veh, freq, check, react, i)

        elif cut_out_veh.pos_profile_lat[i] < wandering_zone:
            mvt.control(ego_veh, stopped_veh, freq, check, react, i)

        li.plot_map_cout_out(vehs, ax1, i, "car_out", live_dir)
        cnt = buildCnt(ego_veh, cut_out_veh, i, ego_veh.cfs, ego_veh.pfs)
        cnt_list.append(cnt)
        if ego_veh.crash == 1:
            break
            fig.patch.set_facecolor((1, 0, 0, 0.2))
        if ego_veh.speed_profile_long[i] == 0:
            ego_veh.pos_profile_long[i:] = ego_veh.pos_profile_long[i]
            ego_veh.speed_profile_long[i:] = 0
            break
    return ego_veh, cut_out_veh, i


def run_one_case(type, res):
    fig = plt.figure()
    plt.axis('off')
    CFS, PFS = [], []
    cnt_list = []

    next_index = getNextIndex()
    dir_name = "./data"
    tmp = type + "_" + next_index
    dir_name = os.path.join(dir_name, tmp)

    if os.path.exists(dir_name) is False:
        os.mkdir(dir_name, 777)

    live_dir = os.path.join(dir_name, "live_dir")

    cnt_xosc = str(next_index) + ".xosc"
    cnt_full_path = os.path.join(dir_name, cnt_xosc)

    full_path_xosc = createXOSC(cnt_xosc, cnt_full_path, res)

    csv_full_path = os.path.join(dir_name, str(next_index) + ".csv")

    remoteCall(full_path_xosc, csv_full_path)

    if type is "cut_in":
        ego_veh, obj_veh, res_dic = cut_in(live_dir, csv_full_path, cnt_list, CFS, PFS,
                                                                          res)
    elif type is "car_following":
        ego_veh, obj_veh, last_index = car_following(live_dir)
    else:
        ego_veh, obj_veh, last_index = cut_out(live_dir)
    """ save"""
    # 生成gif
    # makeGif(live_dir, dir_name, ego_veh.crash, last_index)
    # car driver info
    cnt_pd = pd.DataFrame(cnt_list)
    # sort by cfs_pfs
    sort_cnt_pd = cnt_pd.sort_values(["cfs_pfs", "index"], ascending=[False, False])
    # save info as xlsx
    cntPath = os.path.join(dir_name, type + "_info.xlsx")
    cnt_pd.to_excel(cntPath)
    # save sort as xlsx
    sortPath = os.path.join(dir_name, type + "_sort_info.xlsx")
    sort_cnt_pd.to_excel(sortPath)

    ''' post processing '''
    # plt.figure('Trajectory')
    # plt.plot(obj_veh.pos_profile_long, obj_veh.pos_profile_lat, 'rx', label=type + ' vehicle')
    # plt.plot(ego_veh.pos_profile_long, ego_veh.pos_profile_lat, 'bx', label='Ego vehicle')
    # plt.xlabel('x (m)')
    # plt.ylabel('y (m)')
    # plt.legend()
    # traPath = os.path.join(dir_name, "trajectory.png")
    # plt.savefig(traPath)

    ''' Fuzzy metrics'''
    plt.figure('Fuzzy metrics')
    plt.plot(CFS, 'r', label='CFS')
    plt.plot(PFS, 'b', label='PFS')
    plt.legend()
    resultPath = os.path.join(dir_name, "cfs_pfs.png")
    plt.savefig(resultPath)
    plt.close()
    return res_dic
