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
import random
import numpy as np
import pandas as pd

from utility import real_time_cal

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


def getNormal(x1, x2, low, high):
    while True:
        res = np.random.normal(x1, np.sqrt(x2), 1)[0]
        if res >= low and res <= high:
            break
    return res


def getFromParameterSpace():
    ego_speed = getNormal(55.87, 25, 40, 70)
    obj_speed = getNormal(60, 27, 40, 70)
    while ego_speed <= obj_speed:
        ego_speed = getNormal(55.87, 25, 40, 70)
        obj_speed = getNormal(60, 27, 40, 70)

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
    return res


if __name__ == '__main__':
    # 获取随机参数
    res_list = []
    for i in range(0, 10):
        res = getFromParameterSpace()
        count, max_cfs, last_index = real_time_cal.run_one_case(scenario, res)
        res["count"] = count
        res["max_cfs"] = max_cfs
        res["last_index"] = last_index
        res_list.append(res)
    pd_list = pd.DataFrame(res_list)
    pd_list.to_csv("./result4.csv")
