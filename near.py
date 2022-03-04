import math
import threading
import copy

#用于计算某时刻两辆车的线程
class my_Thread (threading.Thread):
    def __init__(self,xpos1,ypos1,v1,a1,xpos2,ypos2,v2,a2):
        threading.Thread.__init__(self)
        self.xpos1 = xpos1
        self.ypos1 = ypos1
        self.v1 = v1
        self.a1 = a1
        self.xpos2 = xpos2
        self.ypos2 = ypos2
        self.v2 = v2
        self.a2 = a2
        self.R = 50
        self.result = 0
    def run(self):
        self.dis = self.distan()
        if self.dis != 0:
            self.result = self.con_time()

    def get_result(self):
        try:
            return self.result
        except Exception:
            print("错误")

    def distan(self):
        self.distance = math.sqrt(math.pow((self.xpos2-self.xpos1),2)+math.pow((self.ypos2-self.ypos1),2))
        if self.distance <= self.R and self.distance >= 0:
            return 1;
        else:
            return 0;

    def con_time(self):
        self.xv1 = self.v1 * math.sin(self.a1)
        self.yv1 = self.v1 * math.cos(self.a1)

        self.xv2 = self.v2 * math.sin(self.a2)
        self.yv2 = self.v2 * math.cos(self.a2)

        self.a = self.xv2 - self.xv1
        self.b = self.xpos2 - self.xpos1
        self.c = self.yv2 - self.yv1
        self.d = self.ypos2 - self.ypos1
        self.z = ((math.pow(self.a, 2) + math.pow(self.c, 2)) * math.pow(self.R, 2) - pow((self.a * self.d - self.c * self.b), 2))

        if self.z>0:
            self.t = (-1*(self.a*self.b+self.c*self.d)+math.sqrt(self.z))/(pow(self.a,2)+pow(self.c,2))
            self.t = (self.t-100) * 0.5  + 100
        else:
            if self.a1 == self.a2 and self.xv1 and self.xv1 and self.yv1 and self.yv2:
                if self.a1 == 90:
                    self.t = min(((200-self.xpos1)/self.xv1),((200-self.xpos2)/self.xv2))
                elif self.a1 == 270:
                    self.t = min(((0 - self.xpos1) / self.xv1), ((0 - self.xpos2) / self.xv2))
                elif self.a1 == 0:
                    self.t = min(((200 - self.ypos1) / self.yv1), ((200 - self.ypos2) / self.yv2))
                elif self.a1 == 180:
                    self.t = min(((0 - self.ypos1) / self.yv1), ((0 - self.ypos2) / self.yv2))
            else:
                if self.a1 < 45 or self.a1 >= 315:
                    self.t1 = (200 - self.ypos1)/ 3
                elif self.a1 < 135 and self.a1 >= 45:
                    self.t1 = (200 - self.xpos1)/ 3
                elif self.a1 < 225 and self.a1 >= 135:
                    self.t1 = (self.ypos1)/ 3
                elif self.a1 < 315 and self.a1 >= 225:
                    self.t1 = (self.xpos1)/ 3

                if self.a2 < 45 or self.a2 >= 315:
                    self.t2 = (200 - self.ypos2)/ 3
                elif self.a2 < 135 and self.a2 >= 45:
                    self.t2 = (200 - self.xpos2)/ 3
                elif self.a2 < 225 and self.a2 >= 135:
                    self.t2 = (self.ypos2)/ 3
                elif self.a2 < 315 and self.a2 >= 225:
                    self.t2 = (self.xpos2)/ 3
                self.t = min(self.t1 , self.t2)

        return self.t

class near_env():
    def __init__(self,car_state):
        self.car_state = car_state
        self.car_num = len(car_state)

    def run(self):
        T = {}
        N = {}
        t1 = {}
        R = {}
        RX = {}
        RXD = {}
        for each in self.car_state.keys():
            T[each],N[each],t1[each] = self.car_env(each)
        n = copy.deepcopy(N)
        N = self.num_deal(N)
        RX = self.Rx_deal(T, N)
        # print("T:",T)
        # print("N:",N)
        # print("RX:",RX)
        # print("---------------------------------------------------------------------------------------------------------------------------------------")
        return T, N, RX, T, N
        # return T, N, RX


    def car_env(self,id):
        t = {}
        threads = {}
        for each in self.car_state.keys():
            if each == id:
                continue
            else:
                try:
                    thread = my_Thread(self.car_state[id][0][0], self.car_state[id][0][1],
                                       self.car_state[id][1][0], self.car_state[id][1][1],
                                       self.car_state[each][0][0], self.car_state[each][0][1],
                                       self.car_state[each][1][0],
                                       self.car_state[each][1][1])
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
                if threads[each].get_result() != 0:
                    t[each] = threads[each].get_result()
            except:
                continue
        # print("t：",t)
        t1 = copy.deepcopy(t)
        t, n = self.time_deal(t)
        return t,n,t1

    def time_deal(self,t,x = 0.1):
        n = 0
        if len(t):
            Max = max(t.values())
            Min = min(filter(lambda x: x > 0, t.values()))
            if Max == Min:
                for each in t.keys():
                    if t[each] == Max:
                        t[each] = 1
                        n += 1
            else:
                for each in t.keys():
                    if t[each] != 0:
                        t[each] = x + (t[each] - Min) * (1 - x) / (Max - Min)
                        n += 1
        return t,n

    def distant(self,xpos1,ypos1,xpos2,ypos2):
        xpos1 = xpos1
        xpos2 = xpos2
        ypos1 = ypos1
        ypos2 = ypos2
        return math.sqrt(math.pow((xpos2 - xpos1), 2) + math.pow((ypos2 - ypos1), 2))

    def num_deal(self,n,x = 0.1):
        Max = max(n.values())
        Min = min(n.values())
        if Max == 1:
            for each in n.keys():
                n[each] = 0
            return n
        elif Max == Min:
            for each in n.keys():
                n[each] = 1
            return n
        else:
            for each in n.keys():
                if n[each] == 1:
                    n[each] = 0
                else:
                    n[each] = x + (n[each] - Min) * (1 - x) / (Max - Min)
            return n

    def Rx_deal(self,t,n):
        R = {}
        for each1 in t:
            R[each1] = {}
            for each2 in t[each1]:
                R[each1][each2] = (t[each1][each2] * n[each2])
                # R[each1][each2] = (t[each1][each2] * 1)
        return R

# if __name__=="__main__":
#     data = \
#         {1724: [[116.38, 98.46], [7.9, 98.13]], 1726: [[98.4, 117.76], [3.61, 180.0]], 1728: [[98.4, 137.83], [1.16, 180.0]], 1731: [[98.4, 1.82], [15.74, 180.0]], 1732: [[98.4, 146.49], [0.0, 180.0]], 1733: [[98.4, 153.99], [0.03, 180.0]], 1737: [[98.4, 161.57], [0.06, 180.0]], 1738: [[98.4, 38.78], [12.21, 180.0]], 1739: [[89.74, 100.67], [8.2, 294.06]], 1740: [[111.2, 180.26], [18.78, 0.0]], 1743: [[100.83, 88.57], [5.4, 351.87]], 1744: [[98.4, 169.16], [0.09, 180.0]], 1745: [[99.67, 108.54], [0.54, 170.79]], 1746: [[146.21, 88.8], [11.41, 90.0]], 1748: [[98.4, 177.0], [0.28, 180.0]], 1749: [[117.8, 101.6], [0.0, 270.0]], 1750: [[98.4, 128.93], [0.31, 180.0]], 1751: [[82.2, 98.4], [0.0, 90.0]], 1752: [[125.3, 101.6], [0.0, 270.0]], 1753: [[132.8, 101.6], [0.02, 270.0]], 1754: [[140.36, 101.6], [0.1, 270.0]], 1755: [[148.03, 101.6], [0.16, 270.0]], 1756: [[129.47, 111.2], [11.11, 270.0]], 1757: [[50.98, 98.4], [11.92, 90.0]], 1758: [[111.2, 27.08], [8.9, 0.0]], 1759: [[10.95, 95.2], [3.73, 90.0]], 1760: [[111.2, 5.1], [0.0, 0.0]]}
#     near = near_env(data)
#     T, N, RX, n = near.run()
#     print(T[1738])