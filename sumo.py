import os
import sys
import random
import optparse
import time

import numpy as np
import car
import GPSR
import net
import data_run

if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"],"tools")
    sys.path.append(tools)
else:
    sys.exit("无法找到SUMO_HOME环境")
import traci
from sumolib import checkBinary

def sumo_run():
    options = get_options()
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')
    traci.start([sumoBinary, "-c", "D:/Sumo/OSM/2/simu.sumocfg", "--tripinfo-output", "tripinfo.xml", "--start", "--delay","100"])
    car_states = {}
    step = 0
    env1 = car.CarmapEnv()
    con_states = data_run.con_data_get()
    car_states = data_run.car_state_data_get()
    s_t_states = data_run.s_t_data_get()
    while traci.simulation.getMinExpectedNumber() > 0:
        # car_state = car_states[step]
        # s_id = s_t_states[step][0]
        # t_id = s_t_states[step][1]
        # con1 = con_states[step][0]
        # con2 = con_states[step][1]
        # env1.car_state = car_state
        # env1.s_id, env1.t_id = s_id, t_id
        # env1.render(con1, con2)

        car_state = {}
        for each in traci.vehicle.getIDList():
            [xpos,ypos] = traci.vehicle.getPosition(each)
            speed = traci.vehicle.getLateralSpeed(each)
            angle = traci.vehicle.getAngle(each)
            car_state[int(each)] = [[xpos,ypos],[speed,angle]]

        if len(car_state) != 0:
            env1.car_state = car_state
            env1.s_id, env1.t_id = s_t_id(env1.s_id, env1.t_id, env1.car_state)
            if env1.s_id != -1 and env1.t_id != -1:
                con1, con2 = get_con(env1.s_id, env1.t_id, env1.car_state)
                env1.render(con1, con2)
            elif env1.s_id != -1 or env1.t_id != -1:
                env1.render()
            else:
                env1.render()
        car_states[step] = car_state
        traci.simulationStep()
        step += 1
    traci.close()
    return car_states

def s_t_id(s_id,t_id,car_state):
    if len(car_state) >= 2:
        if s_id not in car_state.keys() and t_id not in car_state.keys():
            [s_id, t_id] = random.sample(list(car_state.keys()),2)
        elif s_id not in car_state.keys() and t_id in car_state.keys():
            state = car_state.copy()
            del state[t_id]
            s_id = np.random.choice(list(state.keys()))
        elif s_id in car_state.keys() and t_id not in car_state.keys():
            state = car_state.copy()
            del state[s_id]
            t_id = np.random.choice(list(state.keys()))
    elif len(car_state) == 1:
        s_id = list(car_state.keys())[0]
    return s_id,t_id

def get_con(s_id,t_id,car_state):
    # start1 = time.time()
    env2 = GPSR.GPSR(s_id, t_id, car_state)
    env2.run()
    # start2 = time.time()
    env3 = net.Q_net(s_id, t_id, car_state)
    env3.run()
    # end = time.time()
    # print(s_id,t_id,car_state)
    # print("运行时间：",start2-start1,end-start2)
    return env2.con,env3.env.connect

def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options

if __name__=="__main__":
    car_states = sumo_run()