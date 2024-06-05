import pandapower as pp
import numpy as np


# extract impedance matrix from loaded network file
def impedance_matrix(filename):
    net = pp.converter.from_mpc(filename, f_hz=60)

    # compute the admittance matrix
    pp.runpp(net, numda=False, max_iteration=10)

    matrix_Y = np.array(net._ppc["internal"]["Ybus"].todense())

    # Based on Bolognani's paper, we need to exclude slack bus to get Z
    matrix_Y = matrix_Y[1:, :]
    matrix_Y = matrix_Y[:, 1:]
    matrix_Z = np.linalg.inv(matrix_Y)

    matrix_XX = np.imag(matrix_Z) * 121
    matrix_RR = np.real(matrix_Z) * 121

    return matrix_RR, matrix_XX