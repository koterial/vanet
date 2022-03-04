import logging
import time
import gym
import numpy as np
import random
import math
from gym import spaces
from gym.utils import seeding
import color

logger = logging.getLogger(__name__)

class CarmapEnv(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': 50
    }

    def __init__(self):
        # 设置最大的车流数量
        self.car_num = 3000

        # 设置车道数
        self.lan_num = 8

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
        self.real_con_dis = 30
        self.normalization_maxspeed = self.real_con_dis / self.real_xscale


        #设置最低状态
        self.car_low_state = np.array([
            [self.min_xposition, self.normalization_maxspeed,270],
            [self.min_yposition, self.normalization_maxspeed,180]],
            dtype = np.float64
        )
        #设置最高状态
        self.car_high_state = np.array([
            [self.max_xposition, self.normalization_maxspeed, 90],
            [self.max_yposition, self.normalization_maxspeed, 0]],
            dtype=np.float64
        )

        #设置车辆观测空间（连续BOX）（观察：x位置速度，y位置速度）
        self.car_observation_space = spaces.Box(
            low = self.car_low_state,
            high = self.car_high_state,
            dtype=np.float64
        )

        #设置随即种子
        self.seed()
        self.s_id = -1
        self.t_id = -1
        self.viewer = None
        self.car_state = None
        self.connect_state = None

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def car_step(self, action):
        return self.car_state,{}

    def rans(self):
        self.ran = random.sample(range(self.min_xposition * 1000, self.max_xposition * 1000), self.car_num)
        self.ran2 = self.np_random.uniform(range(0, int(self.normalization_maxspeed * 10000)),self.car_num)

    def reset(self):
        #状态：x位置，y位置，速度大小，速度方向
        reset_state = []
        self.rans()
        for each in range(self.car_num):
            # 八车道十字路口，右侧通行规则
            lane = random.randrange(1,17)
            # 1-8车道用于X轴，1-4向东，5-8向西
            if lane <= 8:
                ypos = (self.border_height + (lane - 1) * self.screen_lan_width + self.screen_lan_width/2) / self.screen_yscale
                if lane <= 4:
                    v = 0
                    xpos = self.ran[each]/1000
                else:
                    v = 180
                    xpos = self.ran[each]/1000
            # 9-16车道用于Y轴，9-13向东，13-16向西
            elif lane >= 9 and lane<=16:
                xpos = (self.border_width + (lane - 9) * self.screen_lan_width + self.screen_lan_width/2) / self.screen_xscale
                if lane <= 13:
                    v = 90
                    ypos = self.ran[each]/1000
                else:
                    v = 270
                    ypos = self.ran[each]/1000
            reset_state.append([[xpos, ypos],[self.ran2[each] / 10000, v]])
        self.car_state = np.array(reset_state)
        return np.array(self.car_state)

    def render(self, connect1=[], connect2=[], c1=(0,0,0), c2=(1,0,0),mode='human'):
        if self.viewer is None:
            from gym.envs.classic_control import rendering
            colors = color.ncolors(self.car_num)
            #生成界面
            self.viewer = rendering.Viewer(self.screen_world_width, self.screen_world_height)

            self.boder1 = rendering.make_polygon([(0,0),(self.border_width,0),(self.border_width,self.border_height),(0,self.border_height)])
            self.boder1.set_color(0.745, 0.745, 0.745)
            self.viewer.add_geom(self.boder1)

            self.boder2 = rendering.make_polygon([(0,0),(self.border_width,0),(self.border_width,self.border_height),(0,self.border_height)])
            self.boder2.set_color(0.745, 0.745, 0.745)
            self.boder2.add_attr(rendering.Transform(translation=(0, self.screen_world_height - self.border_height)))
            self.viewer.add_geom(self.boder2)

            self.boder3 = rendering.make_polygon([(0,0),(self.border_width,0),(self.border_width,self.border_height),(0,self.border_height)])
            self.boder3.set_color(0.745, 0.745, 0.745)
            self.boder3.add_attr(rendering.Transform(translation=(self.screen_world_width - self.border_width, 0)))
            self.viewer.add_geom(self.boder3)

            self.boder4 = rendering.make_polygon([(0,0),(self.border_width,0),(self.border_width,self.border_height),(0,self.border_height)])
            self.boder4.set_color(0.745, 0.745, 0.745)
            self.boder4.add_attr(rendering.Transform(translation=(self.screen_world_width - self.border_width, self.screen_world_height - self.border_height)))
            self.viewer.add_geom(self.boder4)

            #绘制小车
            l, r, t, b = -self.screen_car_width / 2, self.screen_car_width / 2, -self.screen_car_height/2, self.screen_car_height/2
            self.car_name = locals()
            self.cartrans_name = locals()
            for each in range(self.car_num):
                self.car_name['car' + str(each)] = rendering.FilledPolygon([(l, b), (l, t), (r, t), (r, b)])
                # car_name['car' + str(each)].set_color(colors[each][0]/255,colors[each][1]/255,colors[each][2]/255)
                self.car_name['car' + str(each)].set_color(0, 0, 1)

                self.car_name['car' + str(each)].add_attr(rendering.Transform(translation=(0,0)))
                self.cartrans_name['cartrans' + str(each)] = rendering.Transform()
                self.car_name['car' + str(each)].add_attr(self.cartrans_name['cartrans' + str(each)])
                self.viewer.add_geom(self.car_name['car' + str(each)])

        for each in range(self.car_num):
            if each not in self.car_state.keys():
                xpos = -1
                ypos = -1
                self.cartrans_name['cartrans' + str(each)].set_translation(
                    (xpos - self.min_xposition) * self.screen_xscale * 1, (ypos - self.min_yposition) * self.screen_yscale * 1
                )
                self.cartrans_name['cartrans' + str(each)].set_rotation(
                    0 * math.pi
                )
                continue
            if each == self.s_id or each == self.t_id:
                self.car_name['car' + str(each)].set_color(0, 0, 0)
            self.cartrans_name['cartrans' + str(each)].set_rotation(
                ((self.car_state[each][1][1]/180) - 0.5) * math.pi
            )
            xpos = self.car_state[each][0][0] / self.real_xscale
            ypos = self.car_state[each][0][1] / self.real_yscale
            # print("坐标为"+str(xpos)+','+str(ypos))
            # print("坐标为"+str((xpos - self.min_xposition) * self.xscale * 1)+','+str((ypos - self.min_yposition) *  self.yscale * 1))
            self.cartrans_name['cartrans' + str(each)].set_translation(
                (xpos - self.min_xposition) * self.screen_xscale * 1, (ypos - self.min_yposition) * self.screen_yscale * 1
            )

        for each in range(self.lan_num-1):
            if each == int((self.lan_num-1)/2):
                self.viewer.draw_line((0, self.border_height + (each + 1) * self.screen_lan_height),(self.screen_world_height, self.border_height + (each + 1) * self.screen_lan_height),color=(0, 1, 0))
                self.viewer.draw_line((self.border_width + (each + 1) * self.screen_lan_height, 0),(self.border_width + (each + 1) * self.screen_lan_height, self.screen_world_height),color=(0, 1, 0))
            else:
                self.viewer.draw_line((0, self.border_height + (each+1) * self.screen_lan_width), (self.screen_world_width, self.border_height + (each+1) * self.screen_lan_width), color=(0.745, 0.745, 0.745))
                self.viewer.draw_line((self.border_width + (each+1) * self.screen_lan_width, 0), (self.border_width + (each+1) * self.screen_lan_width, self.screen_world_height), color=(0.745, 0.745, 0.745))

        if len(connect1) > 1 and connect1[-1] == self.t_id:
            for each in range(len(connect1)-1):
                if connect1[each] != connect1[each+1]:
                    xpos1 = (self.car_state[connect1[each]][0][0] - self.min_xposition) * self.screen_xscale / self.real_xscale * 1
                    ypos1 = (self.car_state[connect1[each]][0][1] - self.min_yposition) * self.screen_yscale / self.real_yscale * 1
                    xpos2 = (self.car_state[connect1[each+1]][0][0] - self.min_xposition) * self.screen_xscale / self.real_xscale * 1
                    ypos2 = (self.car_state[connect1[each+1]][0][1] - self.min_yposition) * self.screen_yscale / self.real_yscale * 1
                    self.viewer.draw_line((xpos1,ypos1), (xpos2,ypos2), color=c1)

        if len(connect2) > 1 and connect2[-1] == self.t_id:
            for each in range(len(connect2)-1):
                if connect2[each] != connect2[each+1]:
                    xpos1 = (self.car_state[connect2[each]][0][0] - self.min_xposition) * self.screen_xscale / self.real_xscale * 1
                    ypos1 = (self.car_state[connect2[each]][0][1] - self.min_yposition) * self.screen_yscale / self.real_yscale * 1
                    xpos2 = (self.car_state[connect2[each+1]][0][0] - self.min_xposition) * self.screen_xscale / self.real_xscale * 1
                    ypos2 = (self.car_state[connect2[each+1]][0][1] - self.min_yposition) * self.screen_yscale / self.real_yscale * 1
                    self.viewer.draw_line((xpos1,ypos1), (xpos2,ypos2), color=c2)

        return self.viewer.render(return_rgb_array=mode == 'rgb_array')

    def close(self):
        if self.viewer:
            self.viewer.close()
            self.viewer = None