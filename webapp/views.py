from django.shortcuts import render, redirect
# Required library for openseespy analysis
import eqsig.single
from scipy import interpolate
import numpy as np
from openseespy.opensees import *
import math
import optparse
from webapp.uniaxialcalc import *

# Create your views here.
def main_project(request):
    return render(request, 'main.html')
# =========================================================
# src: https://eqsig.readthedocs.io/en/latest/#example 
# =========================================================
def SpecCalcParam(eq1, dt, period):
    periods = np.linspace(0.0, 4, 400)  # period generation for spectrum
    record = eqsig.AccSignal(eq1, dt)   # define record in eqsig
    record.generate_response_spectrum(response_times=periods) # generate response spectrum
    times = record.response_times
    spec = record.s_a
    return (times, spec)
# =========================================================
# here we get motion record(exp: motion_file.txt) to a list for 
# use in time-history analysis 
# =========================================================
def read_ground_motion(filename):
    gm = []
    file_in = open(filename, 'r')
    gm = [float(line) for line in file_in.readlines()]
    return gm

def response_calc(request):
    #=================================================================
    # Get Data
    #=================================================================

    #=================================================================
    # Start Calc
    #=================================================================
    wipe()
    maxNumIter = 150
    Tol = 1e-3
    (hysteretic_paramp , hysteretic_paramn) = uniaxial_param_calc.uniaxialCalc(building_type, seismicity , number_of_stories, user_mass)
    wipe()
    model('basic', '-ndm', 2, '-ndf', 2)
    for k in range(1, number_of_stories + 2):
        if k == 1:
            node(1, 0 , 0)
        else:
            node(k, *[0.0, stories_height[k-2]] , '-mass', *[user_mass[k-2], user_mass[k-2]])
    vals = [1, 1, 1]
    fix(1, *vals)
    for i in range(1, number_of_stories + 1):
        uniaxialMaterial('Hysteretic', i, *hysteretic_paramp[str(i)]['1'], *hysteretic_paramp[str(i)]['2'],
                         *hysteretic_paramp[str(i)]['3'], *hysteretic_paramn[str(i)]['1'] , *hysteretic_paramn[str(i)]['2'], *hysteretic_paramn[str(i)]['3'],
                         pinch_x,pinch_y,0,0,mat_beta)
    for i in range(1, number_of_stories + 1):
        element('zeroLength', i, *[i,i+1], '-mat', *[i,i], '-dir', *[1,2])
        
    #=================================================================
    # Static analysis
    #=================================================================
    constraints('Plain')
    numberer('Plain')
    system('BandGeneral')
    test('NormDispIncr',1.0e-8, 60)
    algorithm('ModifiedNewton')
    integrator('LoadControl', 0.01)
    analysis('Static')
    analyze(100)
    loadConst('-time', 0.0)
    tag1 = 2 * (num - 1) + 1
    tag2 = 2 * (num - 1)
    #==================================================================
    # Rayleigh Calculation
    #==================================================================
    xDamp = damp
    MpropSwitch = 1.0
    KcurrSwitch = 0.0
    KinitSwitch = 0.0
    KcommSwitch = 1.0
    nEigenI = 1
    nEigenJ = n_eigen_j
    lambdaN = eigen('-fullGenLapack', number_of_stories * 2)
    lambdaI = lambdaN[nEigenI-1]
    lambdaJ = lambdaN[nEigenJ-1]
    omegaI = math.pow(lambdaI, 0.5)
    omegaJ = math.pow(lambdaJ, 0.5)
    alphaM = MpropSwitch * xDamp * (2 * omegaI * omegaJ)/(omegaI + omegaJ)
    betaKcurr = KcurrSwitch * 2 * xDamp/(omegaI + omegaJ)
    betaKinit = KinitSwitch * 2 * xDamp/(omegaI + omegaJ)
    betaKcomm = KcommSwitch * 2 * xDamp/(omegaI + omegaJ)
    rayleigh(alphaM, betaKcurr, betaKinit, betaKcomm)
    #==================================================================
    # Period Calculation
    #==================================================================
    W12 = lambdaN[0]
    Tn1 = 2 * 3.14 / (math.pow(W12, 0.5))
    #==================================================================
    # Required Data of Motion 
    #==================================================================
    # !!! Modify
    eq1 = gm_to_list.read_ground_motion("%s" % gm_record_path +"\\%d-1-1.txt" % num) 
    #==================================================================
    # Ground Motion Results Calculation Calculation
    #==================================================================
    gm_dir1 = spectrum_param_calc.SpecCalcParam(eq1, d_t[num], Tn1)
    #==================================================================
    # Time Series
    #==================================================================
    g = 9.80665
    timeSeries('Path', tag1, '-dt', d_t[num], '-values', *eq1)
    pattern('UniformExcitation', tag1, 1, '-accel', tag1, '-factor', g)

    wipeAnalysis()
    constraints('Transformation')
    numberer('RCM')
    system('BandGeneral')

    tCurrent = 0.0
    test_dict = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 3:'EnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algorithm_dict = {1:'KrylovNewton', 2: 'SecantNewton' , 3:'ModifiedNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}
    tFinal = npts[num] * d_t[num]
    
    for i in range(1, number_of_stories+2):
        u1[str(i)] = [0.0]
        v1[str(i)] = [0.0]
        accel1[str(i)] = [0.0]
    for i in range(1, number_of_stories+1):
        d1['%d%d' %(i,i+1)] = [0.0]
    ok = 0
    # print(tCurrent)
    # print(tFinal)
    while tCurrent < tFinal:
        for s in test_dict:
            for j in algorithm_dict: 
                if j < 4:
                    algorithm(algorithm_dict[j], '-initial')
                else:
                    algorithm(algorithm_dict[j])
                while ok == 0 and tCurrent < tFinal:
                    test(test_dict[s], Tol, maxNumIter,0,2)        
                    NewmarkGamma = 0.5
                    NewmarkBeta = 0.25
                    integrator('Newmark', NewmarkGamma, NewmarkBeta)
                    analysis('Transient')
                    ok = analyze(1, d_t[num])
                    if ok == 0 :
                        tCurrent = tCurrent + d_t[num]
                        for i in range(1,number_of_stories+2):
                            u1[str(i)].append(nodeDisp(i,1))
                            v1[str(i)].append(nodeVel(i,1))
                            accel1[str(i)].append(nodeAccel(i,1))
                            reactions('-dynamic', '-rayleight')
                            react1[str(i)].append(nodeReaction(i,1))
                        for i in range(1,number_of_stories+1):
                            d1['%d%d' %(i,i+1)].append((nodeDisp(i+1,1) - nodeDisp(i,1)) / floor_height[i-1])
    for i in range(1,number_of_stories+2):
        disp_dir_1[str(i)] = max(u1[str(i)][:-1], key=abs)
        vel_dir_1[str(i)] = max(v1[str(i)][:-1], key=abs)
        accel_dir_1[str(i)] = accel1[str(i)][:-1]
        reaction_dir_1[str(i)] = max(react1[str(i)][:-1], key=abs)
    for i in range(1,number_of_stories+1):
        drift_dir_1['%d%d' %(i,i+1)] = max(d1['%d%d' %(i,i+1)], key=abs)
    wipe()
    
    return
