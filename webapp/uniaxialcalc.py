import numpy as np
import scipy.linalg 
import math
# =========================================================
# Generate uniaxial hysteretic material parameters
# src: |article|
# "A coarse-grained parallel approach for seismic damage simulations
# of urban areas based on refined models and GPU/CPU cooperative computing"
# =========================================================
# alpha1 & t0(Te): |HAZUS|
# Table 5.5 Code Building Capacity Parameters - Period (Te), Pushover Mode
# Response Factors (alpha1, alpha2)
# ---------------------------------------------------------
# n0(typical number of stories): |HAZUS|
# Table 5.1 Model Building Types
# ---------------------------------------------------------
hazus_basic_data = {'w1l' : {'n0' : 1 , 't0' : 0.35 , 'alpha1' : 0.75 },
                    'w2l' : {'n0' : 2 , 't0' : 0.4 , 'alpha1' : 0.75 },
                    's1l' : {'n0' : 2 , 't0' : 0.5 , 'alpha1' : 0.8 },
                    's1m' : {'n0' : 5 , 't0' : 1.08 , 'alpha1' : 0.8 },
                    's1h' : {'n0' : 13 , 't0' : 2.21 , 'alpha1' : 0.75 },
                    's2l' : {'n0' : 2 , 't0' : 0.4 , 'alpha1' : 0.75 },
                    's2m' : {'n0' : 5 , 't0' : 0.86 , 'alpha1' : 0.75 },
                    's2h' : {'n0' : 13 , 't0' : 1.77 , 'alpha1' : 0.65 },
                    's3l' : {'n0' : 1 , 't0' : 0.4 , 'alpha1' : 0.75 },
                    's4l' : {'n0' : 2 , 't0' : 0.35 , 'alpha1' : 0.75 },
                    's4m' : {'n0' : 5 , 't0' : 0.65 , 'alpha1' : 0.75 },
                    's4h' : {'n0' : 13 , 't0' : 1.32 , 'alpha1' : 0.65 },
                    's5l' : {'n0' : 2 , 't0' : 0.35 , 'alpha1' : 0.75 },
                    's5m' : {'n0' : 5 , 't0' : 0.65 , 'alpha1' : 0.75 },
                    's5h' : {'n0' : 13 , 't0' : 1.32 , 'alpha1' : 0.65 },
                    'c1l' : {'n0' : 2 , 't0' : 0.4 , 'alpha1' : 0.8 },
                    'c1m' : {'n0' : 5 , 't0' : 0.75 , 'alpha1' : 0.8 },
                    'c1h' : {'n0' : 12 , 't0' : 1.45 , 'alpha1' : 0.75 },
                    'c2l' : {'n0' : 2 , 't0' : 0.35 , 'alpha1' : 0.75 },
                    'c2m' : {'n0' : 5 , 't0' : 0.56 , 'alpha1' : 0.75 },
                    'c2h' : {'n0' : 12 , 't0' : 1.09 , 'alpha1' : 0.65 },
                    'c3l' : {'n0' : 2 , 't0' : 0.35 , 'alpha1' : 0.75 },
                    'c3m' : {'n0' : 5 , 't0' : 0.56 , 'alpha1' : 0.75 },
                    'c3h' : {'n0' : 12 , 't0' : 1.09 , 'alpha1' : 0.65 },
                    'pc1l' : {'n0' : 1 , 't0' : 0.35 , 'alpha1' : 0.5 },
                    'pc2l' : {'n0' : 2 , 't0' : 0.35 , 'alpha1' : 0.75 },
                    'pc2m' : {'n0' : 5 , 't0' : 0.56 , 'alpha1' : 0.75 },
                    'pc2h' : {'n0' : 12 , 't0' : 1.09 , 'alpha1' : 0.65 },
                    'rm1l' : {'n0' : 2 , 't0' : 0.35 , 'alpha1' : 0.75 },
                    'rm1m' : {'n0' : 5 , 't0' : 0.56 , 'alpha1' : 0.75 },
                    'rm2l' : {'n0' : 2 , 't0' : 0.35 , 'alpha1' : 0.75 },
                    'rm2m' : {'n0' : 5 , 't0' : 0.56 , 'alpha1' : 0.75 },
                    'rm2h' : {'n0' : 12 , 't0' : 1.09 , 'alpha1' : 0.65 },
                    'urml' : {'n0' : 1 , 't0' : 0.35 , 'alpha1' : 0.5 },
                    'urmm' : {'n0' : 3 , 't0' : 0.5 , 'alpha1' : 0.75 },}
# ---------------------------------------------------------
# SAy, SDy, SAu, SDu calculation: |HAZUS|
# Table 5.7a Code Building Capacity Curves - High-Code Seismic Design Level
# Table 5.7b Code Building Capacity Curves ‐ Moderate‐Code Seismic Design Level
# Table 5.7c Code Building Capacity Curves ‐ Low‐Code Seismic Design Level
# Table 5.7d Building Capacity Curves ‐ Pre‐Code Seismic Design Level
# list data : [SAy, SDy, SAu, SDu]
# ---------------------------------------------------------
backbone_data = {'w1l' : {'H' : [0.4, 0.48, 1.2, 11.51], 'M' : [0.3, 0.36, 0.9, 6.48], 'L' : [0.2, 0.24, 0.6, 4.32], 'Pre' : [0.2, 0.24, 0.6, 4.32]},
                 'w2l' : {'H' : [0.4, 0.63, 1.0, 12.53], 'M' : [0.2, 0.31, 0.5, 4.7], 'L' : [0.1, 0.16, 0.25, 2.35], 'Pre' : [0.1, 0.16, 0.25, 2.35]},
                 's1l' : {'H' : [0.25, 0.61, 0.749, 14.67], 'M' : [0.125, 0.31, 0.375, 5.5], 'L' : [0.062, 0.15, 0.187, 2.29], 'Pre' : [0.062, 0.15, 0.187, 2.75]},
                 's1m' : {'H' : [0.156, 1.78, 0.468, 28.4], 'M' : [0.078, 0.89, 0.234, 10.65], 'L' : [0.039, 0.44, 0.117, 4.44], 'Pre' : [0.039, 0.44, 0.117, 5.33]},
                 's1h' : {'H' : [0.098, 4.66, 0.293, 55.88], 'M' : [0.049, 2.33, 0.147, 20.96], 'L' : [0.024, 1.16, 0.073, 8.73], 'Pre' : [0.024, 1.16, 0.073, 10.48]},
                 's2l' : {'H' : [0.4, 0.63, 0.8, 10.02], 'M' : [0.2, 0.31, 0.4, 3.76], 'L' : [0.1, 0.16, 0.2, 1.57], 'Pre' : [0.1, 0.16, 0.2, 1.88]},
                 's2m' : {'H' : [0.333, 2.43, 0.667, 25.88], 'M' : [0.167, 1.21, 0.333, 9.7], 'L' : [0.083, 0.61, 0.167, 4.05], 'Pre' : [0.083, 0.61, 0.167, 4.85]},
                 's2h' : {'H' : [0.254, 7.75, 0.508, 61.97], 'M' : [0.127, 3.87, 0.254, 23.24], 'L' : [0.063, 1.94, 0.127, 9.68], 'Pre' : [0.063, 1.94, 0.127, 11.62]},
                 's3l' : {'H' : [0.4, 0.63, 0.8, 10.2], 'M' : [0.2, 0.31, 0.4, 3.76], 'L' : [0.1, 0.16, 0.2, 1.57], 'Pre' : [0.1, 0.16, 0.2, 1.88]},
                 's4l' : {'H' : [0.32, 0.38, 0.72, 6.91], 'M' : [0.19, 0.16, 0.36, 2.59], 'L' : [0.08, 0.1, 0.18, 1.08], 'Pre' : [0.08, 0.1, 0.18, 1.3]},
                 's4m' : {'H' : [0.267, 1.09, 0.6, 13.10], 'M' : [0.133, 0.55, 0.3, 4.91], 'L' : [0.067, 0.27, 0.15, 2.05], 'Pre' : [0.067, 0.27, 0.15, 2.46]},
                 's4h' : {'H' : [0.203, 3.49, 0.457, 31.37], 'M' : [0.102, 1.74, 0.228, 11.76], 'L' : [0.051, 0.87, 0.114, 4.9], 'Pre' : [0.051, 0.87, 0.114, 5.88]},
                 's5l' : {'H' : [None, None, None, None], 'M' : [None, None, None, None], 'L' : [0.1, 0.12, 0.2, 1.2], 'Pre' : [0.1, 0.12, 0.2, 1.2]},
                 's5m' : {'H' : [None, None, None, None], 'M' : [None, None, None, None], 'L' : [0.083, 0.34, 0.167, 2.27], 'Pre' : [0.083, 0.34, 0.167, 2.27]},
                 's5h' : {'H' : [None, None, None, None], 'M' : [None, None, None, None], 'L' : [0.063, 1.09, 0.127, 5.45], 'Pre' : [0.063, 1.09, 0.127, 5.45]},
                 'c1l' : {'H' : [0.25, 0.39, 0.749, 9.39], 'M' : [0.125, 0.2, 0.375, 3.52], 'L' : [0.062, 0.1, 0.187, 1.47], 'Pre' : [0.062, 0.1, 0.187, 1.76]},
                 'c1m' : {'H' : [0.208, 1.15, 0.624, 18.44], 'M' : [0.104, 0.58, 0.312, 6.91], 'L' : [0.052, 0.29, 0.156, 2.88], 'Pre' : [0.052, 0.29, 0.156, 3.46]},
                 'c1h' : {'H' : [0.098, 2.01, 0.293, 24.13], 'M' : [0.049, 1.01, 0.147, 9.05], 'L' : [0.024, 0.5, 0.073, 3.77], 'Pre' : [0.024, 0.5, 0.073, 4.52]},
                 'c2l' : {'H' : [0.4, 0.48, 1, 9.59], 'M' : [0.2, 0.24, 0.5, 3.6], 'L' : [0.1, 0.12, 0.25, 1.5], 'Pre' : [0.1, 0.12, 0.25, 1.8]},
                 'c2m' : {'H' : [0.333, 1.04, 0.833, 13.84], 'M' : [0.167, 0.52, 0.417, 5.19], 'L' : [0.083, 0.26, 0.208, 2.16], 'Pre' : [0.083, 0.26, 0.208, 2.6]},
                 'c2h' : {'H' : [0.254, 2.94, 0.635, 29.39], 'M' : [0.127, 1.47, 0.317, 11.02], 'L' : [0.063, 0.74, 0.159, 4.59], 'Pre' : [0.063, 0.74, 0.159, 5.51]},
                 'c3l' : {'H' : [None, None, None, None], 'M' : [None, None, None, None], 'L' : [0.1, 0.12, 0.225, 1.35], 'Pre' : [0.1, 0.12, 0.225, 1.35]},
                 'c3m' : {'H' : [None, None, None, None], 'M' : [None, None, None, None], 'L' : [0.083, 0.26, 0.188, 1.95], 'Pre' : [0.083, 0.26, 0.188, 1.95]},
                 'c3h' : {'H' : [None, None, None, None], 'M' : [None, None, None, None], 'L' : [0.063, 0.74, 0.143, 4.13], 'Pre' : [0.063, 0.74, 0.143, 4.13]},
                 'pc1l' : {'H' : [0.6, 0.72, 1.2, 11.51], 'M' : [0.3, 0.36, 0.6, 4.32], 'L' : [0.15, 0.18, 0.3, 1.8], 'Pre' : [0.15, 0.18, 0.3, 2.16]},
                 'pc2l' : {'H' : [0.4, 0.48, 0.8, 7.67], 'M' : [0.2, 0.24, 0.4, 2.88], 'L' : [0.1, 0.12, 0.2, 1.2], 'Pre' : [0.1, 0.12, 0.2, 1.44]},
                 'pc2m' : {'H' : [0.333, 1.04, 0.667, 11.07], 'M' : [0.167, 0.52, 0.333, 4.15], 'L' : [0.083, 0.26, 0.167, 1.73], 'Pre' : [0.083, 0.26, 0.167, 2.08]},
                 'pc2h' : {'H' : [0.254, 2.94, 0.508, 23.52], 'M' : [0.127, 1.47, 0.254, 8.82], 'L' : [0.063, 0.74, 0.127, 3.67], 'Pre' : [0.063, 0.74, 0.127, 4.41]},
                 'rm1l' : {'H' : [0.533, 0.64, 1.066, 10.23], 'M' : [0.267, 0.32, 0.533, 3.84], 'L' : [0.133, 0.16, 0.267, 1.6], 'Pre' : [0.133, 0.16, 0.267, 1.92]},
                 'rm1m' : {'H' : [0.444, 1.38, 0.889, 14.76], 'M' : [0.222, 0.69, 0.444, 5.54], 'L' : [0.111, 0.35, 0.222, 2.31], 'Pre' : [0.111, 0.35, 0.222, 2.77]},
                 'rm2l' : {'H' : [0.533, 0.64, 1.066, 10.23], 'M' : [0.267, 0.32, 0.533, 3.84], 'L' : [0.133, 0.16, 0.267, 1.6], 'Pre' : [0.133, 0.16, 0.267, 1.92]},
                 'rm2m' : {'H' : [0.444, 1.38, 0.889, 14.76], 'M' : [0.222, 0.69, 0.444, 5.54], 'L' : [0.111, 0.35, 0.222, 2.31], 'Pre' : [0.111, 0.35, 0.222, 2.77]},
                 'rm2h' : {'H' : [0.338, 3.92, 0.667, 31.35], 'M' : [0.169, 1.96, 0.338, 11.76], 'L' : [0.085, 0.98, 0.169, 4.9], 'Pre' : [0.085, 0.98, 0.169, 5.88]},
                 'urml' : {'H' : [None, None, None, None], 'M' : [None, None, None, None], 'L' : [0.2, 0.24, 0.4, 2.4], 'Pre' : [0.2, 0.24, 0.4, 2.4]},
                 'urmm' : {'H' : [None, None, None, None], 'M' : [None, None, None, None], 'L' : [0.111, 0.27, 0.222, 1.81], 'Pre' : [0.111, 0.27, 0.222, 1.81]},}

def uniaxialCalc(building_type, seismicity, number_of_stories, mass):
    hysteretic_paramp = {}
    hysteretic_paramn = {}
    k = np.zeros((number_of_stories, number_of_stories))
    m = np.zeros((number_of_stories, number_of_stories))
    for i in range(0,number_of_stories):
        for j in range(0, number_of_stories):
            if i == j:
                k[i,j] = 2 * 1
                m[i,j] = mass[i]
            if i == j and i == number_of_stories - 1:
                k[i,j] = 1
            if j == (i+1) or j == (i-1):
                k[i,j] = -1
    eigvals, eigvects = scipy.linalg.eig(k,m)
    if number_of_stories != 1:
        omega = math.sqrt(np.absolute(min(eigvals)))
        mode_shape_coeff = k - (omega ** 2) * m
        mode_shape_coeff = np.delete(mode_shape_coeff, -1, 0)
        coeff = mode_shape_coeff[:, :-1]
        b = -1 * mode_shape_coeff[:, -1]
        mode_shape = np.linalg.inv(coeff) * b
        mode_shape_final = mode_shape[:, -1]
        mode_shape_final = np.append(mode_shape_final, 1)
        mode_shape_final_transpose = mode_shape_final.reshape(-1, 1)
        mode_shape_final = np.asmatrix(mode_shape_final)
        mode_shape_final_transpose = np.asmatrix(mode_shape_final_transpose)
    else:
        mode_shape_final = 1
        mode_shape_final_transpose = 1
    lmbda = (mode_shape_final * np.asmatrix(k) * mode_shape_final_transpose) / (mode_shape_final * mode_shape_final_transpose)
    lmbda = 1 / lmbda
    n_0 = hazus_basic_data[building_type]['n0']
    t_0 = hazus_basic_data[building_type]['t0']
    alpha_1 = hazus_basic_data[building_type]['alpha1']
    s_a_y = backbone_data[building_type][seismicity][0]
    s_d_y = backbone_data[building_type][seismicity][1] * 0.0254
    s_a_u = backbone_data[building_type][seismicity][2]
    s_d_u = backbone_data[building_type][seismicity][3] * 0.0254
    beta = s_a_u / s_a_y
    etta = ((s_a_u - s_a_y) / (s_d_u - s_d_y)) * (s_d_y / s_a_y)
    t_1 = (number_of_stories / n_0) * t_0
    for i in range(1, number_of_stories + 1):
        k_0 = lmbda * mass[i-1] * (4 * math.pi ** 2) / (t_1 ** 2)
        v_y_1 = s_a_y * alpha_1 * mass[i-1] * 9.8086 * number_of_stories * (1 - (i * (i-1)) / (number_of_stories * (number_of_stories + 1)))
        v_y_2 = beta * v_y_1
        v_y_3 = v_y_2
        delta_1 = v_y_1 / k_0[0,0]
        delta_2 = (v_y_2 - v_y_1) / (etta * k_0[0,0]) + delta_1
        delta_3 = 1
        hysteretic_paramp[str(i)] = {'1' : [v_y_1 , delta_1] , '2' : [v_y_2 , delta_2] , '3' : [v_y_3 , delta_3]}
        hysteretic_paramn[str(i)] = {'1' : [-v_y_1 , -delta_1] , '2' : [-v_y_2 , -delta_2] , '3' : [-v_y_3 , -delta_3]}
    return (hysteretic_paramp , hysteretic_paramn)

