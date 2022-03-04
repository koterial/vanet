import time
from collections import defaultdict
import numpy as np
import packets
import sumo

class Q_net():
    def __init__(self, s_id, t_id, car_state):
        self.car_state = car_state
        self.car_num = len(car_state)
        self.s_id = s_id
        self.t_id = t_id
        self.env = packets.PacketEnv(self.car_state)
        self.lr, self.factor = 0.7, 0.9
        self.episode = 300
        self.epsilon = 1
        self.score_list = []
        self.step = 0
        self.id_deal()

    def id_deal(self):
        self.id_list = list(self.car_state.keys())
        self.Q = defaultdict(lambda: np.zeros(len(self.id_list)))


    def run(self):
        for each in range(self.episode):
            self.step += 1
            s = tuple(self.env.reset(self.s_id, self.t_id))
            if len(self.env.RX[self.s_id].keys()) == 0 or len(self.env.RX[self.t_id].keys()) == 0:
                # print("节点无法连接")
                break
            score = 0
            for i in range(len(self.car_state)):
                if np.random.random() > each * 4 / self.episode:
                    a = np.random.choice(range(len(self.id_list)))
                else:
                    a = np.argmax(self.Q[s])
                # a = self.id_list[a]
                next_s, reward, done, _ = self.env.step(self.id_list[a])
                next_s = tuple(next_s)
                score += reward
                self.Q[s][a] = (1 - self.lr) * self.Q[s][a] + self.lr * (reward + self.factor * max(self.Q[next_s]))
                s = next_s
                # self.env.render()
                if done:
                    self.score_list.append(score)
                    # print("第", each, "次获得分数：", score, "当前最高分数：", max(self.score_list), self.env.connect)
                    break
                if i == len(self.car_state) - 1 and not done:
                    self.score_list.append(score)
                    # print("第", each, "次获得分数：", score, "当前最高分数：", max(self.score_list), self.env.connect)
                    self.env.connect = [self.env.s_id]
                    break
            if len(self.score_list) >= 10:
                if (all(self.score_list[-10:] == np.linspace(self.score_list[-1], self.score_list[-1], 10))):
                    break
        # print(env.Q)
        # print(self.score_list)
        self.env.close()
        # print("本次寻径次数", self.step)

if __name__ == "__main__":
    # Q = defaultdict(lambda: np.zeros(3000))
    data = \
        {1250: [[98.4, 117.8], [0.0, 180.0]], 1299: [[98.4, 140.31], [0.0, 180.0]], 1302: [[148.59, 101.6], [0.0, 270.0]], 1332: [[98.4, 147.81], [0.01, 180.0]], 1343: [[98.4, 170.46], [0.22, 180.0]], 1345: [[71.02, 98.4], [2.45, 90.0]], 1364: [[98.4, 125.3], [0.0, 180.0]], 1373: [[98.4, 132.8], [0.0, 180.0]], 1377: [[98.4, 162.89], [0.06, 180.0]], 1382: [[95.2, 172.96], [0.0, 180.0]], 1384: [[98.4, 180.54], [0.0, 180.0]], 1386: [[95.2, 180.46], [0.01, 180.0]], 1388: [[98.4, 155.33], [0.02, 180.0]], 1390: [[98.4, 188.07], [0.04, 180.0]], 1392: [[95.2, 132.21], [0.0, 180.0]], 1399: [[95.2, 139.73], [0.14, 180.0]], 1408: [[92.0, 178.36], [0.0, 180.0]], 1419: [[88.8, 117.8], [0.0, 180.0]], 1421: [[88.8, 125.3], [0.0, 180.0]], 1424: [[88.8, 132.8], [0.0, 180.0]], 1427: [[44.69, 98.4], [0.0, 90.0]], 1428: [[92.0, 185.87], [0.0, 180.0]], 1435: [[92.0, 117.93], [2.63, 180.0]], 1436: [[92.0, 133.8], [7.92, 180.0]], 1442: [[95.2, 160.3], [3.35, 180.0]], 1443: [[88.8, 180.38], [7.22, 180.0]], 1444: [[88.8, 194.9], [0.0, 180.0]], 1461: [[87.29, 98.98], [5.22, 83.28]], 1466: [[61.06, 98.4], [0.07, 90.0]], 1471: [[37.19, 98.4], [0.0, 90.0]], 1482: [[141.09, 101.6], [0.0, 270.0]], 1505: [[69.38, 101.6], [6.89, 270.0]], 1509: [[163.6, 101.6], [0.0, 270.0]], 1513: [[53.25, 98.4], [1.06, 90.0]], 1516: [[110.6, 92.0], [9.84, 90.0]], 1518: [[29.69, 98.4], [0.0, 90.0]], 1521: [[111.45, 88.8], [9.45, 90.0]], 1522: [[73.17, 95.2], [1.12, 90.0]], 1523: [[88.74, 83.61], [6.41, 153.54]], 1526: [[61.19, 95.2], [0.0, 90.0]], 1527: [[75.79, 88.8], [4.49, 90.0]], 1530: [[53.62, 95.2], [1.13, 90.0]], 1531: [[63.32, 88.8], [2.86, 90.0]], 1547: [[156.1, 101.6], [0.0, 270.0]], 1548: [[171.1, 101.6], [0.0, 270.0]], 1550: [[178.6, 101.6], [0.0, 270.0]], 1554: [[108.09, 100.05], [0.02, 258.4]], 1557: [[132.57, 101.6], [1.02, 270.0]], 1567: [[52.63, 88.8], [0.43, 90.0]], 1568: [[115.29, 100.18], [1.17, 251.95]], 1578: [[90.45, 92.0], [7.09, 90.0]], 1582: [[44.94, 95.2], [0.0, 90.0]], 1585: [[75.08, 92.0], [4.77, 90.0]], 1587: [[22.19, 98.4], [0.0, 90.0]], 1589: [[122.2, 104.8], [1.78, 270.0]], 1591: [[61.98, 92.0], [1.66, 90.0]], 1592: [[111.2, 136.09], [9.39, 0.0]], 1593: [[44.69, 88.8], [0.0, 90.0]], 1595: [[37.19, 88.8], [0.0, 90.0]], 1597: [[89.45, 108.0], [10.12, 270.0]], 1598: [[37.42, 95.2], [0.0, 90.0]], 1601: [[104.18, 111.2], [8.45, 270.0]], 1602: [[29.69, 88.8], [0.0, 90.0]], 1606: [[131.82, 104.8], [1.19, 270.0]], 1607: [[140.52, 104.8], [0.52, 270.0]], 1609: [[110.25, 108.0], [6.49, 270.0]], 1610: [[124.72, 108.0], [5.01, 270.0]], 1611: [[101.6, 74.7], [0.0, 0.0]], 1612: [[148.8, 104.8], [0.0, 270.0]], 1616: [[156.38, 104.8], [0.0, 270.0]], 1617: [[22.19, 88.8], [0.0, 90.0]], 1618: [[101.6, 52.19], [0.01, 0.0]], 1619: [[121.15, 111.2], [6.21, 270.0]], 1621: [[14.69, 88.8], [0.0, 90.0]], 1627: [[136.16, 111.2], [3.18, 270.0]], 1628: [[29.88, 95.2], [0.0, 90.0]], 1631: [[101.6, 37.15], [0.1, 0.0]], 1635: [[52.67, 92.0], [0.48, 90.0]], 1636: [[22.37, 95.2], [0.0, 90.0]], 1638: [[14.69, 98.4], [0.0, 90.0]], 1639: [[163.9, 104.8], [0.0, 270.0]], 1640: [[146.89, 111.2], [0.92, 270.0]], 1641: [[171.4, 104.8], [0.0, 270.0]], 1642: [[138.09, 108.0], [1.82, 270.0]], 1643: [[178.91, 104.8], [0.0, 270.0]], 1644: [[186.1, 101.6], [0.0, 270.0]], 1646: [[7.19, 88.8], [0.0, 90.0]], 1648: [[147.58, 108.0], [0.23, 270.0]], 1651: [[155.31, 111.2], [0.0, 270.0]], 1653: [[162.81, 111.2], [0.0, 270.0]], 1657: [[163.27, 108.0], [0.0, 270.0]], 1659: [[186.48, 104.8], [0.0, 270.0]], 1661: [[101.6, 59.69], [0.0, 0.0]], 1664: [[187.75, 108.0], [0.0, 270.0]], 1665: [[191.87, 111.2], [0.0, 270.0]], 1668: [[101.6, 82.2], [0.0, 0.0]], 1673: [[101.6, 67.2], [0.0, 0.0]], 1687: [[101.6, 44.68], [0.02, 0.0]], 1692: [[104.8, 67.54], [0.0, 0.0]], 1716: [[111.2, 82.2], [0.0, 0.0]], 1718: [[101.6, 29.5], [0.12, 0.0]], 1725: [[111.2, 74.7], [0.0, 0.0]], 1731: [[104.8, 83.2], [0.0, 0.0]], 1736: [[108.0, 82.2], [0.0, 0.0]], 1738: [[101.6, 21.72], [0.54, 0.0]], 1739: [[104.8, 37.3], [5.61, 0.0]], 1740: [[108.0, 74.57], [0.25, 0.0]], 1743: [[104.8, 53.47], [7.87, 0.0]], 1746: [[111.2, 37.67], [11.05, 0.0]], 1758: [[111.2, 12.05], [4.44, 0.0]]}
    # [1547, 1642, 1639, 1550]
    env = Q_net(1547, 1550, data)
    env.run()
    # print(env.env.connect)