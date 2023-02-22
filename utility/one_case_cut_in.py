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

import imageio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from post_processing import live_graph as li
from . import movement as mvt
from . import models as md
from . import global_parameters as gp


def buildCnt(ego_veh, cut_in_veh, index, cfs, pfs):
    cnt = {}
    cnt["index"] = index
    cnt["ego_speed_profile_long"] = ego_veh.speed_profile_long[index]
    cnt["ego_speed_profile_lat"] = ego_veh.speed_profile_lat[index]
    cnt["ego_pos_profile_long"] = ego_veh.pos_profile_long[index]
    cnt["ego_pos_profile_lat"] = ego_veh.pos_profile_lat[index]
    cnt["cut_in_ego_speed_profile_long"] = cut_in_veh.speed_profile_long[index]
    cnt["cnt_in_ego_speed_profile_lat"] = cut_in_veh.speed_profile_lat[index]
    cnt["cnt_in_ego_pos_profile_long"] = cut_in_veh.pos_profile_long[index]
    cnt["cnt_in_ego_pos_profile_lat"] = cut_in_veh.pos_profile_lat[index]
    cnt["cfs"] = cfs
    cnt["pfs"] = pfs
    cnt["cfs_pfs"] = cfs + pfs

    return cnt


def getNextIdnex():
    f = open('./index.txt', encoding='utf-8')
    line = f.readlines()[-1].strip()  # 读取第一行
    f.close()
    next_index = str(int(line) + 1)
    f = open('./index.txt', 'a+', encoding='utf-8')
    f.writelines('\n' + next_index)
    f.close()
    return next_index


def makeGif(live_dir, dir_name, isCrash, last_index):
    gif_list = []
    for i in range(last_index + 1):
        image_path = str(i) + ".png"
        gif_list.append(imageio.imread(os.path.join(live_dir, image_path)))
    git_path = os.path.join(dir_name, str(isCrash) + ".gif")
    imageio.mimwrite(git_path, gif_list, fps=1)


def run_one_case(type):
    length = gp.length
    width = gp.width
    iterations = gp.iterations
    freq = gp.freq


    init_long_speed_ego = gp.initial_speed
    init_long_speed_c = gp.obstacle_speed
    lateral_speed = gp.lateral_speed
    long_dist = gp.front_distance

    print('Starting speed cut in: ' + str(init_long_speed_ego) + ' (km/h)')
    print('Obstacle speed cut in: ' + str(init_long_speed_c) + ' (km/h)')
    print('Lateral speed cut in: ' + str(lateral_speed) + ' (m/s)')
    print('Front distance cut in: ' + str(long_dist) + ' (m)')

    init_long_speed_c = init_long_speed_c / 3.6
    init_long_speed_ego = init_long_speed_ego / 3.6

    init_pos_c = np.array([long_dist + length, 1.6 + width])
    init_pos_ego = np.array([0, 0])


    cut_in_veh = mvt.create_profile_cutting_in(init_pos_c, init_long_speed_c, lateral_speed, iterations, freq)

    ego_veh = mvt.create_profile_cutting_in(init_pos_ego, init_long_speed_ego, 0, iterations, freq)

    cut_in_veh.width = width
    cut_in_veh.length = length
    ego_veh.width = width
    ego_veh.length = length

    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    plt.axis('off')
    vehs = [ego_veh, cut_in_veh]
    CFS, PFS = [], []

    cnt_list = []

    next_index = getNextIdnex()
    dir_name = "./data"
    tmp = type + "_" + next_index
    dir_name = os.path.join(dir_name, tmp)

    if os.path.exists(dir_name) is False:
        os.mkdir(dir_name, 777)

    live_dir = os.path.join(dir_name, "live_dir")
    last_index = -1
    for i in range(iterations - 1):

        if i == 1:
            plt.pause(2)


        cfs, pfs = mvt.control(ego_veh, cut_in_veh, freq, check, react, i)
        # build cnt info
        cnt = buildCnt(ego_veh, cut_in_veh, i, cfs, pfs)
        cnt_list.append(cnt)
        CFS.append(cfs)
        PFS.append(pfs)

        li.plot_map(vehs, ax1, i, live_dir)
        last_index = i
        if ego_veh.crash == 1:
            break
            fig.patch.set_facecolor((1, 0, 0, 0.2))

    """ save"""
    # 生成gif
    makeGif(live_dir, dir_name, ego_veh.crash, last_index)
    # car driver info
    cnt_pd = pd.DataFrame(cnt_list)
    # sort by cfs_pfs
    sort_cnt_pd = cnt_pd.sort_values(["cfs_pfs", "index"], ascending=[False, False])
    # save info as xlsx
    cntPath = os.path.join(dir_name, "car_info.xlsx")
    cnt_pd.to_excel(cntPath)
    # save sort as xlsx
    sortPath = os.path.join(dir_name, "sort_info.xlsx")
    sort_cnt_pd.to_excel(sortPath)

    ''' post processing '''
    plt.figure('Trajectory')
    plt.plot(cut_in_veh.pos_profile_long, cut_in_veh.pos_profile_lat, 'rx', label='Cut-in vehicle')
    plt.plot(ego_veh.pos_profile_long, ego_veh.pos_profile_lat, 'bx', label='Ego vehicle')
    plt.xlabel('x (m)')
    plt.ylabel('y (m)')
    plt.legend()
    traPath = os.path.join(dir_name, "trajectory.png")
    plt.savefig(traPath)

    ''' Fuzzy metrics'''
    plt.figure('Fuzzy metrics')
    plt.plot(CFS, 'r', label='CFS')
    plt.plot(PFS, 'b', label='PFS')
    plt.legend()
    resultPath = os.path.join(dir_name, "cfs_pfs.png")
    plt.savefig(resultPath)
