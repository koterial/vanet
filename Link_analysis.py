import math
import numpy as np
import data_run
import near
import net
import Excel
import pickle
import matplotlib.pyplot as plt
from multiprocessing import Pool

class Link_analysis():
    def __init__(self,car_state,con):
        self.car_state = car_state
        self.car_num = len(car_state)
        self.con = con
        self.con_dis = 300
        self.min_xposition = 0
        self.max_xposition = 1
        self.min_yposition = 0
        self.max_yposition = 1
        # 屏幕尺寸
        self.screen_height = 800
        self.screen_width = 1200
        # 世界尺度
        self.world_height = self.max_yposition - self.min_yposition
        self.world_width = self.max_xposition - self.min_xposition
        # 归一化世界尺度和屏幕尺度（x轴,y轴）
        self.xscale = self.screen_width / self.world_width
        self.yscale = self.screen_height / self.world_height

    def run(self):
        # print(self.con)
        _,_,_,self.T,self.N = near.near_env(self.car_state).run()
        # print(self.T)
        # print(self.N)
        self.single_t , self.min_t = self.single_t_analysis()
        self.single_n, self.min_n = self.single_n_analysis()
        # print("平均中继链路时间:",self.single_t)
        # print("实际链路持续时间:", self.min_t)
        # print("平均中继节点因子:", self.single_n)
        # print("最小中继节点因子:", self.min_n)

    def single_t_analysis(self):
        t = []
        if len(self.con) == 1:
            return 0, 0
        for each in range(len(self.con)-1):
            t.append(self.T[self.con[each]][self.con[each+1]])
        sum_t = np.sum(np.array(t))
        min_t = min(t)
        return sum_t/(len(self.con)-1),min_t

    def single_n_analysis(self):
        n = []
        if len(self.con) == 1:
            return 0, 0
        for each in range(len(self.con) - 1):
            n.append(self.N[self.con[each]])
        sum_n = np.sum(np.array(n))
        min_n = min(n)
        return sum_n / (len(self.con) - 1), min_n

def analysis1(car_states, con_states, x=0):
    mean_t = []
    min_t = []
    mean_n = []
    min_n = []
    for each in car_states:
        print("当前进度",100 * each/len(car_states))
        # print("正在分析链路",x,"：",con_states[each][x])
        analysis = Link_analysis(car_states[each],con_states[each][x])
        analysis.run()
        mean_t.append(analysis.single_t)
        min_t.append(analysis.min_t)
        mean_n.append(analysis.single_n)
        min_n.append(analysis.min_n)
    return mean_t,min_t,mean_n,min_n

def analysis2(car_state, s_id, t_id):
    env = net.Q_net(s_id, t_id, car_state)
    env.run()
    if len(env.score_list) <= 0:
        return 0,0
    score = env.score_list[-1]
    max_score = max(env.score_list)
    return score, max_score

if __name__ == "__main__":
    # car_states = data_run.car_state_data_get()
    # con_states = data_run.con_data_get()
    #
    # res_list = []
    # pool = Pool(2)
    # res = pool.apply_async(analysis1, args=(car_states, con_states, 0,))
    # res_list.append(res)
    # res = pool.apply_async(analysis1, args=(car_states, con_states, 1,))
    # res_list.append(res)
    # pool.close()
    # pool.join()
    # GPSR_mean_t, GPSR_min_t,GPSR_mean_n, GPSR_min_n = res_list[0].get()
    # Q_mean_t, Q_min_t,Q_mean_n, Q_min_n = res_list[1].get()
    #
    # print("GPSR平均节点数量：", np.mean(GPSR_mean_n), "，最小节点数量：", np.mean(GPSR_min_n),"平均连接时间：", np.mean(GPSR_mean_t), "，最小连接时间：", np.mean(GPSR_min_t))
    # print("强化学习平均节点数量：", np.mean(Q_mean_n), "，最小节点数量：", np.mean(Q_min_n),"平均连接时间：", np.mean(Q_mean_t), "，最小连接时间：", np.mean(Q_min_t))


    car_states = data_run.car_state_data_get()
    s_t_states = data_run.s_t_data_get()
    file = Excel.excel_file()
    for each in car_states:
        if s_t_states[each][0] != -1 and s_t_states[each][1] != -1:
            score, max_score = analysis2(car_states[each], s_t_states[each][0], s_t_states[each][1])
            print(each, score, max_score)
            file.write([each, len(car_states[each]), score, max_score])
    file.save()
    file.wb.close()