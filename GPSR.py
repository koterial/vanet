import math
import numpy
import pickle
import threading

class MyThread(threading.Thread):
    def __init__(self, xpos1, ypos1, xpos2, ypos2):
        threading.Thread.__init__(self)
        self.xpos1 = xpos1
        self.ypos1 = ypos1
        self.xpos2 = xpos2
        self.ypos2 = ypos2
        self.R = 50

    def run(self):
        self.result = self.distan()

    def distan(self):
        distance = math.sqrt(math.pow((self.xpos2-self.xpos1),2)+math.pow((self.ypos2-self.ypos1),2))
        if distance <= self.R and distance >= 0:
            return distance;
        else:
            return -1;

    def get_result(self):
        try:
            return self.result
        except Exception:
            print("错误")


class GPSR():
    def __init__(self,s_id,t_id,car_state):
        self.car_state = car_state
        self.car_num = len(car_state)
        self.s_id = s_id
        self.t_id = t_id
        self.packet = self.s_id
        self.con = []

    def run(self):
        self.near_list = {}
        self.connect()
        if len(self.car_state) <= 1:
            return self.con
        for each in self.car_state.keys():
            self.near_list[each] = self.car_env(each)
        # print(self.near_list)
        self.t_distance = self.target_distance()
        self.greed_connect()
        # print(self.s_id, self.t_id, self.con, self.near_list)

    def car_env(self, id):
        near_list = {}
        threads = {}
        for each in self.car_state.keys():
            if each == id:
                continue
            else:
                try:
                    thread = MyThread(self.car_state[id][0][0], self.car_state[id][0][1],self.car_state[each][0][0], self.car_state[each][0][1])
                    threads[each] = thread
                except:
                    print("线程" + str(each) + "添加失败")
                    continue
        for each in threads.keys():
            try:
                threads[each].start()
            except:
                print("线程" + str(each) + "启动失败")
                continue
        for each in threads.keys():
            try:
                threads[each].join()
            except:
                print("线程" + str(each) + "阻塞失败")
                continue
        for each in threads.keys():
            try:
                if threads[each].get_result() != -1:
                    near_list[each] = threads[each].get_result()
            except:
                continue
        return near_list

    def connect(self):
        self.con.append(self.packet)
        # print(self.near_list[packet])

    def greed_connect(self):
        for each in self.car_state.keys():
            t_distance = {}
            # 直接连接
            # print(self.packet,self.near_list[self.packet].keys())
            if self.t_id in self.near_list[self.packet].keys():
                self.packet = self.t_id
                self.connect()
                break
            # 无法继续连接
            elif (len(self.near_list[self.packet].keys()) <= 1 and len(self.con) != 1):
                self.con = [self.s_id]
                break
            elif (len(self.near_list[self.packet].keys()) == 0 and len(self.con) == 1):
                self.con = [self.s_id]
                break
            elif set(self.con) >= set(self.near_list[self.packet].keys()):
                self.con = [self.s_id]
                break
            else:
                # 计算邻居节点距离目标节点的距离
                for each in (self.near_list[self.packet].keys()):
                    t_distance[each] = self.t_distance[each]
                t_distance[self.packet] = self.t_distance[self.packet]
                if self.packet != min(t_distance, key=t_distance.get) and min(t_distance, key=t_distance.get) not in self.con:
                    self.packet = min(t_distance, key=t_distance.get)
                    self.connect()
                elif self.packet == min(t_distance, key=t_distance.get):
                    if self.empty_connect() not in self.con:
                        self.packet = self.empty_connect()
                        self.connect()
                    else:
                        pass
        if self.con[-1] != self.t_id:
            self.con = [self.s_id]

    def empty_connect(self):
        # 无法直接链接到目标节点，并且当前节点为最近节点，进入路由空洞，采取周边模式
        # print("路由空洞")
        keys = {}
        angle_list = {}
        angle = self.angle(self.car_state[self.packet][0][0],self.car_state[self.packet][0][1],self.car_state[self.t_id][0][0],self.car_state[self.t_id][0][1])
        if angle < 0:
            angle += 360
        # 获取邻居节点的角度
        for each in (self.near_list[self.packet].keys()):
            angle_list[each] = self.angle(self.car_state[self.packet][0][0],self.car_state[self.packet][0][1],self.car_state[each][0][0],self.car_state[each][0][1])
            if angle_list[each] < angle:
                angle_list[each] += 360
        # 计算邻居节点的角度差
        ang = lambda x: x - angle
        for key,value in angle_list.items():
            keys[key] = ang(value)
        if min(keys, key=keys.get) in self.con:
            # print(min(keys, key=keys.get))
            del keys[min(keys, key=keys.get)]
        # print(keys)
        return min(keys, key=keys.get)

    def angle(self,xpos1,ypos1,xpos2,ypos2):
        xpos1 = xpos1
        ypos1 = ypos1
        xpos2 = xpos2
        ypos2 = ypos2
        dx = xpos2 - xpos1
        dy = ypos2 - ypos1
        angle = math.atan2(dy, dx) * 180 / math.pi
        return angle

    def target_distance(self):
        distance = {}
        xpos2 = self.car_state[self.t_id][0][0]
        ypos2 = self.car_state[self.t_id][0][1]
        for each in self.car_state.keys():
            if each != self.t_id:
                xpos1 = self.car_state[each][0][0]
                ypos1 = self.car_state[each][0][1]
                distance[each] = math.sqrt(math.pow((xpos2 - xpos1), 2) + math.pow((ypos2 - ypos1), 2))
        return distance

    def get_result(self):
        try:
            return self.con
        except Exception:
            print("错误")

if __name__ == "__main__":
    data = \
        {1594: [[99.07, 93.54], [1.9, 339.65]], 1604: [[101.6, 145.69], [9.54, 0.0]],
         1608: [[101.4, 84.59], [0.0, 357.71]], 1610: [[117.8, 111.2], [0.0, 270.0]],
         1611: [[101.6, 77.11], [0.0, 0.0]], 1612: [[117.8, 101.6], [0.0, 270.0]], 1616: [[125.3, 101.6], [0.0, 270.0]],
         1617: [[82.2, 88.8], [0.0, 90.0]], 1618: [[101.6, 69.61], [0.0, 0.0]], 1619: [[125.3, 111.2], [0.0, 270.0]],
         1620: [[31.88, 111.2], [14.04, 270.0]], 1621: [[74.7, 88.8], [0.0, 90.0]],
         1622: [[92.0, 67.74], [20.88, 180.0]], 1623: [[98.4, 129.8], [12.77, 180.0]],
         1624: [[111.2, 63.94], [14.84, 0.0]], 1625: [[111.2, 26.89], [8.03, 0.0]],
         1626: [[88.8, 182.47], [6.27, 180.0]], 1627: [[192.61, 108.0], [2.29, 270.0]]}
    # [[1616, 1619, 1617, 1619, 1594, 1619], [1616]]
    env = GPSR(1616, 1627, data)
    env.run()
    print(env.con)