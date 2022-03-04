import random
import time
import pickle
import numpy as np
import car
import xml.dom.minidom
import GPSR
import net
from multiprocessing import Pool

num = '_3'

def car_state_data_get():
    dom = xml.dom.minidom.parse('simu'+ num +'.xml')
    root = dom.documentElement
    times = root.getElementsByTagName('timestep')
    car_states = {}
    step = 0
    for time in times:
        vehicles = time.getElementsByTagName('vehicle')
        car_state = {}
        if len(vehicles) == 0:
            continue
        for vehicle in vehicles:
            id = int(vehicle.getAttribute('id'))
            xpos = float(vehicle.getAttribute('x'))
            ypos = float(vehicle.getAttribute('y'))
            speed = float(vehicle.getAttribute('speed'))
            angle = float(vehicle.getAttribute('angle'))
            car_state[id] = [[xpos, ypos], [speed, angle]]
        car_states[step] = car_state
        step += 1
    print('状态数据导入')
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
        t_id = -1
    return s_id,t_id

def s_t_data_save(car_states):
    [s_id,t_id] = [-1,-1]
    s_t = {}
    for each in car_states:
        s_id, t_id = s_t_id(s_id, t_id, car_states[each])
        s_t[each]=[s_id,t_id]
    with open('s_t_state'+ num +'.pickle', 'wb') as f:
        pickle.dump(s_t, f)
        print('节点状态已保存')

def s_t_data_get():
    with open('s_t_state'+ num +'.pickle', 'rb') as f:
        s_t_states = pickle.load(f)
        print('节点数据导入')
    # print(s_t_states)
    return s_t_states

def get_con(s_id,t_id,car_state,each = -1):
    if s_id != -1 and t_id != -1:
        # print(s_id, t_id,car_state, each)
        env2 = GPSR.GPSR(s_id, t_id, car_state)
        env2.run()
        env3 = net.Q_net(s_id, t_id, car_state)
        env3.run()
        print(each, env2.con, env3.env.connect)
        return env2.con, env3.env.connect, each
    elif s_id != -1 or t_id != -1:
        return [s_id],[s_id],each
    else:
        return [s_id],[s_id],each

def con_data_save(car_states,s_t_state):
    cons = {}
    res_list = []
    pool = Pool(14)
    for each in car_states:
        res = pool.apply_async(get_con, args=(s_t_state[each][0],s_t_state[each][1],car_states[each],each,))
        res_list.append(res)
    pool.close()
    pool.join()
    for res in res_list:
        each = res.get()[2]
        cons[each] = [res.get()[0],res.get()[1]]
        # print([res.get()[0],res.get()[1]])
    with open('con_state'+ num +'.pickle', 'wb') as f:
        pickle.dump(cons, f)
        print('链接状态已保存')
    # print(cons)

def con_data_get():
    with open('con_state'+ num +'.pickle', 'rb') as f:
        con_states = pickle.load(f)
        print('链接数据导入')
    return con_states

def data_run1(car_states):
    env1 = car.CarmapEnv()
    for each in car_states:
        env1.car_state = car_states[each]
        env1.s_id, env1.t_id = s_t_id(env1.s_id, env1.t_id, env1.car_state)
        if env1.s_id != -1 and env1.t_id != -1:
            con1,con2,_ = get_con(env1.s_id,env1.t_id,env1.car_state)
            env1.render(con1,con2)
        elif env1.s_id != -1 or env1.t_id != -1:
            env1.render()
        else:
            env1.render()

def data_run2(car_states,st_states,con_states):
    env1 = car.CarmapEnv()
    for each in car_states:
        env1.car_state = car_states[each]
        env1.s_id = st_states[each][0]
        env1.t_id = st_states[each][1]
        con1 = con_states[each][0]
        con2 = con_states[each][1]
        env1.render(con1,con2)

def data_save():
    car_states = car_state_data_get()
    # s_t_data_save(car_states)
    s_t_states = s_t_data_get()
    con_data_save(car_states, s_t_states)

def start():
    car_states = car_state_data_get()
    s_t_states = s_t_data_get()
    con_states = con_data_get()
    data_run2(car_states, s_t_states, con_states)

if __name__=="__main__":
    # data_save()
    start()