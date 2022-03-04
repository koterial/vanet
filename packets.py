# 状态为位置速度信息，方便拓展，占用内存较大，搭配net_v3使用
import time
import gym
import numpy as np
import random
import math
from gym import spaces
from gym.utils import seeding
import color
import near
import sumo

class PacketEnv(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': 30
    }

    def __init__(self,car_state):
        # 设置最大的车流数量
        self.car_num = 3000

        # 设置车道数
        self.lan_num = 8

        self.s_id = -1
        self.t_id = -1
        self.packets = -1
        self.connect = []

        # 屏幕世界尺寸
        self.screen_world_width = 800
        self.screen_world_height = 800

        # 实际世界尺寸（车道宽度为3.2）
        self.real_world_width = 200
        self.real_world_height = 200
        self.real_lane_width = 3.2
        self.real_lane_height = 3.2
        # 实际车辆尺寸（长3，宽3）
        self.real_car_width = 3
        self.real_car_height = 3

        # 归一化尺寸
        self.min_xposition = 0
        self.max_xposition = 1
        self.min_yposition = 0
        self.max_yposition = self.real_world_height / self.real_world_width
        self.normalization_world_width = self.max_xposition - self.min_xposition
        self.normalization_world_height = self.max_yposition - self.min_yposition

        # 屏幕尺寸和归一化尺寸之比（x轴,y轴）
        self.screen_xscale = self.screen_world_width / self.normalization_world_width
        self.screen_yscale = self.screen_world_height / self.normalization_world_height

        # 实际尺寸和归一化尺寸之比（x轴,y轴）
        self.real_xscale = self.real_world_width / self.normalization_world_width
        self.real_yscale = self.real_world_height / self.normalization_world_height

        # 屏幕车辆,车道尺寸
        self.screen_car_width = self.screen_xscale * self.real_car_width / self.real_xscale
        self.screen_car_height = self.screen_yscale * self.real_car_height / self.real_yscale
        self.screen_lan_width = self.screen_xscale * self.real_lane_width / self.real_xscale
        self.screen_lan_height = self.screen_yscale * self.real_lane_width / self.real_yscale
        self.border_width = (self.screen_world_width / 2) - (self.lan_num / 2) * self.screen_lan_width
        self.border_height = (self.screen_world_height / 2) - (self.lan_num / 2) * self.screen_lan_height

        # 设置最大速度
        self.real_maxspeed = 16.6667
        self.real_minspeed = 0.0
        self.normalization_maxspeed = self.real_maxspeed / self.real_xscale
        self.normalization_minspeed = self.real_minspeed / self.real_xscale
        # 设置最大通信距离
        self.real_con_dis = 50
        self.normalization_maxspeed = self.real_con_dis / self.real_xscale

        self.car_state = car_state
        self.T,self.N,self.RX,_,_ = near.near_env(self.car_state).run()

        self.seed()
        self.viewer = None

        self.action_space = list(self.car_state.keys())
        # for each in self.RX.keys():
        #     self.action_space[each] = list(self.RX[each].keys())

        self.low_state = np.array([
            [0, 0, self.real_minspeed, 0, 0, 0],
            [0, 0, self.real_minspeed, 90, 0, 0],
            [0, 0, self.real_minspeed, 180, 0, 0],
            [0, 0, self.real_minspeed, 270, 0, 0]],
            dtype=np.float64
        )
        self.high_state = np.array([
            [0, 0, self.real_maxspeed, 0, 0, 0],
            [0, 0, self.real_maxspeed, 90, 0, 0],
            [0, 0, self.real_maxspeed, 180, 0, 0],
            [0, 0, self.real_maxspeed, 270, 0, 0]],
            dtype=np.float64
        )
        self.observation_space = spaces.Box(
            low=self.low_state,
            high=self.high_state,
            dtype=np.float64
        )

    def step(self, action):
        done = bool(self.t_id == action and action in self.RX[self.packets].keys())
        # done = bool(self.t_id == action)
        if action == self.packets or action in self.connect or action not in self.RX[self.packets].keys():
            reward = -10.0
        else:
            reward = self.RX[self.packets][action]-2
            RXD = self.distant(self.car_state[action][0][0], self.car_state[action][0][1],self.car_state[self.t_id][0][0], self.car_state[self.t_id][0][1])
            if done:
                RXD = 2.0
                reward += RXD + 10.0
            else:
                if RXD >= self.real_con_dis:
                    RXD = (self.real_con_dis / RXD) * 1
                else:
                    RXD = 1.5 - 0.5 * RXD / self.real_con_dis
                reward += RXD
        if action not in self.RX[self.packets].keys():
            pass
        else:
            self.connect.append(action)
            self.packets = action
            self.state = (self.car_state[action][0][0],self.car_state[action][0][1],self.car_state[action][1][0],self.car_state[action][1][1],self.car_state[self.t_id][0][0],self.car_state[self.t_id][0][1])
        return np.array(self.state), reward, done, {}



    def distant(self,xpos1,ypos1,xpos2,ypos2):
        xpos1 = xpos1
        xpos2 = xpos2
        ypos1 = ypos1
        ypos2 = ypos2
        return math.sqrt(math.pow((xpos2 - xpos1), 2) + math.pow((ypos2 - ypos1), 2))


    def render(self, mode='human'):
        if self.viewer is None:
            from gym.envs.classic_control import rendering
            colors = color.ncolors(self.car_num)
            # 生成界面
            self.viewer = rendering.Viewer(self.screen_world_width, self.screen_world_height)

            self.boder1 = rendering.make_polygon([(0, 0), (self.border_width, 0), (self.border_width, self.border_height), (0, self.border_height)])
            self.boder1.set_color(0.745, 0.745, 0.745)
            self.viewer.add_geom(self.boder1)

            self.boder2 = rendering.make_polygon([(0, 0), (self.border_width, 0), (self.border_width, self.border_height), (0, self.border_height)])
            self.boder2.set_color(0.745, 0.745, 0.745)
            self.boder2.add_attr(rendering.Transform(translation=(0, self.screen_world_height - self.border_height)))
            self.viewer.add_geom(self.boder2)

            self.boder3 = rendering.make_polygon([(0, 0), (self.border_width, 0), (self.border_width, self.border_height), (0, self.border_height)])
            self.boder3.set_color(0.745, 0.745, 0.745)
            self.boder3.add_attr(rendering.Transform(translation=(self.screen_world_width - self.border_width, 0)))
            self.viewer.add_geom(self.boder3)

            self.boder4 = rendering.make_polygon([(0, 0), (self.border_width, 0), (self.border_width, self.border_height), (0, self.border_height)])
            self.boder4.set_color(0.745, 0.745, 0.745)
            self.boder4.add_attr(rendering.Transform(translation=(
            self.screen_world_width - self.border_width, self.screen_world_height - self.border_height)))
            self.viewer.add_geom(self.boder4)

            # 绘制小车
            l, r, t, b = -self.screen_car_width / 2, self.screen_car_width / 2, -self.screen_car_height / 2, self.screen_car_height / 2
            self.car_name = locals()
            self.cartrans_name = locals()
            for each in range(self.car_num):
                self.car_name['car' + str(each)] = rendering.FilledPolygon([(l, b), (l, t), (r, t), (r, b)])
                # car_name['car' + str(each)].set_color(colors[each][0]/255,colors[each][1]/255,colors[each][2]/255)
                self.car_name['car' + str(each)].set_color(0, 0, 1)

                self.car_name['car' + str(each)].add_attr(rendering.Transform(translation=(0, 0)))
                self.cartrans_name['cartrans' + str(each)] = rendering.Transform()
                self.car_name['car' + str(each)].add_attr(self.cartrans_name['cartrans' + str(each)])
                self.viewer.add_geom(self.car_name['car' + str(each)])

            for each in range(self.car_num):
                if each not in self.car_state.keys():
                    xpos = -1
                    ypos = -1
                    self.cartrans_name['cartrans' + str(each)].set_translation((xpos - self.min_xposition) * self.screen_xscale * 1,(ypos - self.min_yposition) * self.screen_yscale * 1)
                    self.cartrans_name['cartrans' + str(each)].set_rotation(0 * math.pi)
                    continue
                if each == self.s_id or each == self.t_id:
                    self.car_name['car' + str(each)].set_color(0, 0, 0)
                self.cartrans_name['cartrans' + str(each)].set_rotation(((self.car_state[each][1][1] / 180) - 0.5) * math.pi)
                xpos = self.car_state[each][0][0] / self.real_xscale
                ypos = self.car_state[each][0][1] / self.real_yscale
                # print("坐标为"+str(xpos)+','+str(ypos))
                # print("坐标为"+str((xpos - self.min_xposition) * self.xscale * 1)+','+str((ypos - self.min_yposition) *  self.yscale * 1))
                self.cartrans_name['cartrans' + str(each)].set_translation((xpos - self.min_xposition) * self.screen_xscale * 1,(ypos - self.min_yposition) * self.screen_yscale * 1)

        for each in range(self.lan_num - 1):
            if each == int((self.lan_num - 1) / 2):
                self.viewer.draw_line((0, self.border_height + (each + 1) * self.screen_lan_height), (self.screen_world_height, self.border_height + (each + 1) * self.screen_lan_height), color=(0, 1, 0))
                self.viewer.draw_line((self.border_width + (each + 1) * self.screen_lan_height, 0), (self.border_width + (each + 1) * self.screen_lan_height, self.screen_world_height), color=(0, 1, 0))
            else:
                self.viewer.draw_line((0, self.border_height + (each + 1) * self.screen_lan_width), (self.screen_world_width, self.border_height + (each + 1) * self.screen_lan_width),color=(0.745, 0.745, 0.745))
                self.viewer.draw_line((self.border_width + (each + 1) * self.screen_lan_width, 0), (self.border_width + (each + 1) * self.screen_lan_width, self.screen_world_height),color=(0.745, 0.745, 0.745))


        if len(self.connect) > 1:
            # print(self.connect)
            for each in range(len(self.connect) - 1):
                if self.connect[each] != self.connect[each + 1]:
                    xpos1 = (self.car_state[self.connect[each]][0][0] - self.min_xposition) * self.screen_xscale / self.real_xscale * 1
                    ypos1 = (self.car_state[self.connect[each]][0][1] - self.min_yposition) * self.screen_yscale / self.real_yscale * 1
                    xpos2 = (self.car_state[self.connect[each + 1]][0][0] - self.min_xposition) * self.screen_xscale / self.real_xscale * 1
                    ypos2 = (self.car_state[self.connect[each + 1]][0][1] - self.min_yposition) * self.screen_yscale / self.real_yscale * 1
                    self.viewer.draw_line((xpos1, ypos1), (xpos2, ypos2), color=(1,0,0))

        return self.viewer.render(return_rgb_array=mode == 'rgb_array')

    def reset(self,s_id,t_id,):
        self.connect = []
        self.s_id = s_id
        self.t_id = t_id
        self.packets = self.s_id
        self.connect.append(self.packets)
        self.state = (self.car_state[self.packets][0][0], self.car_state[self.packets][0][1], self.car_state[self.packets][1][0],self.car_state[self.packets][1][1], self.car_state[self.t_id][0][0], self.car_state[self.t_id][0][1])
        return np.array(self.state)

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def close(self):
        if self.viewer:
            self.viewer.close()
            self.viewer = None



if __name__ =="__main__":
    # 测试环境
    data = {1: [[192.33, 98.4], [17.1, 90.0]], 11: [[116.57, 98.55], [2.43, 195.07]], 13: [[178.61, 92.0], [17.93, 90.0]], 14: [[98.4, 117.8], [0.0, 180.0]], 15: [[98.4, 125.3], [0.0, 180.0]], 16: [[101.6, 82.2], [0.0, 0.0]], 18: [[98.4, 132.8], [0.0, 180.0]], 19: [[98.4, 140.3], [0.0, 180.0]], 20: [[111.2, 82.2], [0.0, 0.0]], 21: [[81.69, 101.6], [3.3, 315.41]], 22: [[103.21, 88.8], [18.68, 90.0]], 23: [[58.95, 98.4], [13.83, 90.0]], 24: [[101.6, 40.23], [9.75, 0.0]], 25: [[175.08, 101.6], [7.42, 270.0]], 26: [[188.24, 104.8], [4.3, 270.0]], 27: [[111.2, 5.1], [0.0, 0.0]], 4: [[149.63, 98.4], [11.17, 90.0]], 5: [[101.6, 179.18], [17.39, 0.0]], 6: [[191.94, 88.8], [20.32, 90.0]], 8: [[101.6, 129.59], [11.07, 0.0]]}
    env = PacketEnv(data)
    while True:
        s_id, t_id = sumo.s_t_id(env.s_id, env.t_id, env.car_state)
        env.reset(s_id,t_id)
        score = 0
        for each in range(len(data)):
            # if len(env.action_space[env.packets]) == 0:
            #     score += -10
            #     done = False
            #     s = env.car_state
            #     break
            action = random.choice(env.action_space)
            s, reward, done, _ = env.step(action)
            score += reward
            env.render()
        print(env.connect)
        print(score)
        env.close()