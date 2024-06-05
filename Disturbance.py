import pandapower as pp
import numpy as np
import pandas as pd
from Dynamics1 import impedance_matrix
import random

#filename = 'Online Ctrl/case34sa_mod.mat'
filename = 'case34sa_mod.mat'
matrix_R, matrix_X = impedance_matrix(filename)


### import load and pv data
#file_load = 'Online Ctrl/data_Load.csv'
file_load = 'data_Load.csv'

data_load = pd.read_csv(file_load, index_col=0)
load_p = np.array(data_load.loc[:, 'Total load']) * 2
load_q = load_p * 0.5

#file_pv = 'Online Ctrl/data_PV2.csv'
file_pv = 'data_PV.csv'
data_pv = pd.read_csv(file_pv, index_col=0)
data_pv = np.array(data_pv.loc[:, 'PV medium output']) * 2


### deploy pv randomly
random.seed(12)
node_list = list(range(1,34))

pv1_num = 3  # 250kVA
pv2_num = 8  # 300kVA
pv3_num = 5  # 350kVA

pv_1 = random.sample(node_list, pv1_num)

remaining_elements = [elem for elem in node_list if elem not in pv_1]
pv_2 = random.sample(remaining_elements, pv2_num)

remaining_elements = [elem for elem in remaining_elements if elem not in pv_2]
pv_3 = random.sample(remaining_elements, pv3_num)

remaining_elements = [elem for elem in remaining_elements if elem not in pv_3]


net = pp.converter.from_mpc(filename, f_hz=60)
net_load_p = net.load.loc[:, 'p_mw'].values

def cal_disturbance(time):
    # interval t=[1, 19524]
    factor_load = load_p[time] / 3.09
    load_p_now = net_load_p * factor_load
    load_q_now = load_p_now * 0.5

    output_pv_now = np.ones(len(load_p_now))
    for i in range(33):
        if i+1 in pv_1:
            output_pv_now[i] = (250 / 4900) * data_pv[time]
        elif i+1 in pv_2:
            output_pv_now[i] = (300 / 4900) * data_pv[time]
        elif i+1 in pv_3:
            output_pv_now[i] = (350 / 4900) * data_pv[time]


    factor_load = load_p[time-1] / 3.09

    load_p_before = net_load_p * factor_load
    load_q_before = load_p_before * 0.5

    output_pv_before = np.ones(len(load_p_now))
    for i in range(33):
        if i+1 in pv_1:
            output_pv_before[i] = (250 / 4900) * data_pv[time-1]
        elif i+1 in pv_2:
            output_pv_before[i] = (300 / 4900) * data_pv[time-1]
        elif i+1 in pv_3:
            output_pv_before[i] = (350 / 4900) * data_pv[time-1]
    
    w = (matrix_R @ (output_pv_now - output_pv_before + load_p_before - load_p_now) 
         + matrix_X @ (load_q_before - load_q_now)) / 11
 
    return w