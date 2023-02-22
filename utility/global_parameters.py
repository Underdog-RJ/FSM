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

### global parameters shared among models and simulations ###

# vehicle dimensions
length = 4.3
width = 1.9

# simulation parameters
iterations = 150
freq = 5
wandering_zone = -0.375
g = 9.81

# ego_veh
initial_speed = 50
obstacle_speed = 20
lateral_speed = -3
front_distance = 50

# xosc properties
ego_longitudeSpeed = 60
obj_longitudeSpeed = 51
Distance_ds_triggerValue = 13
ego_startPositionS = 50
obj_startPositionS = 150
laneChangeDuration = 2.2
