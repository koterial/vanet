# import numpy as np
# import xml.dom.minidom
# import car
import Excel
#
# dom = xml.dom.minidom.parse('simu.xml')
#
# root = dom.documentElement
#
# times = root.getElementsByTagName('timestep')
#
# car_states = {}
#
# env1 = car.CarmapEnv()
#
# step = 0
# for time in times:
#     vehicles = time.getElementsByTagName('vehicle')
#     car_state = {}
#     for vehicle in vehicles:
#         id = int(vehicle.getAttribute('id'))
#         xpos = float(vehicle.getAttribute('x'))
#         ypos = float(vehicle.getAttribute('y'))
#         speed = float(vehicle.getAttribute('speed'))
#         angle = float(vehicle.getAttribute('angle'))
#         car_state[id] = [[xpos,ypos],[speed,angle]]
#     env1.car_state = car_state
#     env1.render()
#     car_states[step] = car_state
#     step += 1

# for each in car_states.keys():
#     print(car_states[each])
#     deal = near.near_env(car_states[each], 1, 1)
#     deal.run()

# class data_read():
#     def __init__(self,time,file = 'simu.xml'):
#         self.time = time
#         self.file = file
#
#     def run(self):
#         dom = xml.dom.minidom.parse(self.file)
#         root = dom.documentElement
#         times = root.getElementsByTagName('timestep')
#         vehicles = root.getElementsByTagName('vehicle')
import data_run

con_states = data_run.con_data_get()
# car_states = data_run.car_state_data_get()
# s_t_states = data_run.s_t_data_get()
file = Excel.excel_file2()
for each in con_states:
    file.write([each, len(con_states[each][0]), len(con_states[each][1])])
file.save()
file.wb.close()
# print(s_t_states[each])
# print(car_states[each])
print("---------------------------------------------------------------")