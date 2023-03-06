'''Functions relevant to vehicle movement'''

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

from . import vehicle as vi
import numpy as np
import warnings
import pandas as pd


def create_veh_from_csv(csv_path):
    cnt_pd = pd.read_csv(csv_path, header=6)
    length = len(cnt_pd)
    ego_veh = vi.vehicle()
    ego_speed_profile_long = []
    ego_speed_profile_lat = []
    ego_pos_profile_long = []
    ego_pos_profile_lat = []
    obj_veh = vi.vehicle()
    obj_speed_profile_long = []
    obj_speed_profile_lat = []
    obj_pos_profile_long = []
    obj_pos_profile_lat = []
    for row_index, row in cnt_pd.iterrows():
        ego_pos_profile_long.append(row[" #1 World_Position_Y [m] "])
        ego_pos_profile_lat.append(row[" #1 World_Position_X [m] "])
        ego_speed_profile_long.append(row[" #1 Vel_Y [m/s] "])
        ego_speed_profile_lat.append(row[" #1 Vel_X [m/s] "])
        obj_pos_profile_long.append(row[" #2 World_Position_Y [m] "])
        obj_pos_profile_lat.append(row[" #2 World_Position_X [m] "])
        obj_speed_profile_long.append(row[" #2 Vel_Y [m/s] "])
        obj_speed_profile_lat.append(row[" #2 Vel_X [m/s] "])
    ego_veh.speed_profile_long = ego_speed_profile_long
    ego_veh.speed_profile_lat = ego_speed_profile_lat
    ego_veh.pos_profile_long = ego_pos_profile_long
    ego_veh.pos_profile_lat = ego_pos_profile_lat
    obj_veh.speed_profile_long = obj_speed_profile_long
    obj_veh.speed_profile_lat = obj_speed_profile_lat
    obj_veh.pos_profile_long = obj_pos_profile_long
    obj_veh.pos_profile_lat = obj_pos_profile_lat
    return ego_veh, obj_veh, length


def create_profile_cutting_in(init_pos, init_long_speed, lateral_speed, iterations, freq):
    speed_profile_long = np.array([init_long_speed] * iterations)
    if lateral_speed != 0:
        cut_in_duration = int(np.abs(freq * init_pos[1]) // np.abs(lateral_speed) + 1)
        speed_profile_lat = np.array(
            [lateral_speed] * cut_in_duration + [0] * (iterations - cut_in_duration))
    else:
        speed_profile_lat = np.array([0.] * iterations)
    speed_profile_lat = speed_profile_lat[:iterations]
    pos_profile_long = speed_profile_long.cumsum() / freq + init_pos[0]
    pos_profile_lat = speed_profile_lat.cumsum() / freq + init_pos[1]

    veh = vi.vehicle()

    veh.speed_profile_lat = speed_profile_lat
    veh.speed_profile_long = speed_profile_long
    veh.pos_profile_lat = pos_profile_lat
    veh.pos_profile_long = pos_profile_long

    return veh


def create_profile_decel(init_pos, deceleration, init_long_speed, iterations, freq):  ###NO JERK no nothing

    # speed_profile_long = np.array([init_long_speed] * iterations)
    speed_profile_long = np.array(init_long_speed - np.arange(0, iterations, 1) * deceleration / freq)
    speed_profile_long[speed_profile_long < 0] = 0
    speed_profile_lat = np.array([0] * iterations)

    pos_profile_long = speed_profile_long.cumsum() / freq + init_pos[0]
    pos_profile_lat = speed_profile_lat.cumsum() / freq + init_pos[1]

    veh = vi.vehicle()
    veh.speed_profile_lat = speed_profile_lat
    veh.speed_profile_long = speed_profile_long
    veh.pos_profile_lat = pos_profile_lat
    veh.pos_profile_long = pos_profile_long

    return veh


def control(ego_veh, cutting_in_veh, freq, model_check, model_react, i):
    speed_log = ego_veh.speed_profile_long[i]
    speed_lat = ego_veh.speed_profile_lat[i]

    safe, cfs, pfs = model_check(ego_veh, cutting_in_veh, speed_log, speed_lat, freq, i)

    # if safe and ego_veh.safe:
    #     new_speed_long = min(ego_veh.speed_profile_long[i + 1], speed_log + ego_veh.max_a_CF / freq)
    #     new_speed_long = max(new_speed_long, speed_log - ego_veh.max_a_CF / freq)
    #
    #     new_speed_lat = min(ego_veh.speed_profile_lat[i + 1], speed_lat + ego_veh.max_a_lat / freq)
    #     new_speed_lat = max(new_speed_lat, speed_lat - ego_veh.max_a_lat / freq)
    #
    # elif safe and not ego_veh.safe:
    #     new_speed_long, new_speed_lat = speed_log, speed_lat
    #
    # else:
    #     new_speed_long, new_speed_lat = model_react(ego_veh, speed_log, freq)
    #     ego_veh.safe = False
    #
    # ego_veh.speed_profile_long[i + 1] = new_speed_long
    # ego_veh.speed_profile_lat[i + 1] = new_speed_lat
    #
    # ego_veh.pos_profile_long[i + 1] = ego_veh.pos_profile_long[i] + new_speed_long / freq
    # ego_veh.pos_profile_lat[i + 1] = ego_veh.pos_profile_lat[i] + new_speed_lat / freq

    # if abs(ego_veh.pos_profile_lat[i] - cutting_in_veh.pos_profile_lat[i]) + \
    #         - ego_veh.width / 2 - cutting_in_veh.width / 2 < 0:
    #     ego_veh.crash_type = 1
    #     ego_veh.crash = True
    # if abs(ego_veh.pos_profile_long[i] - cutting_in_veh.pos_profile_long[i]) - ego_veh.length / 2 + \
    #         - cutting_in_veh.length / 2 < 0:
    #     ego_veh.crash_type = 2
    #     ego_veh.crash = True

    if abs(ego_veh.pos_profile_lat[i] - cutting_in_veh.pos_profile_lat[i]) + \
            - ego_veh.width / 2 - cutting_in_veh.width / 2 < 0 and \
            abs(ego_veh.pos_profile_long[i] - cutting_in_veh.pos_profile_long[i]) - ego_veh.length / 2 + \
            - cutting_in_veh.length / 2 < 0:
        if not ego_veh.crash:


            if ego_veh.pos_profile_long[i] > cutting_in_veh.pos_profile_long[i]:
                ego_veh.crash_type = 1
            else:
                ego_veh.crash_type = 2
        ego_veh.crash = True

    return cfs, pfs
