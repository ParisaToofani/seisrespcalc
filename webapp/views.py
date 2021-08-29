from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
# Required library for openseespy analysis
import eqsig.single
import math
import optparse
import numpy as np
from scipy import interpolate
from openseespy.opensees import *
from webapp.uniaxialcalc import *
from loaddb.models import PinchingData

# =========================================================
# here we get motion record(exp: motion_file.txt) to a list for 
# use in time-history analysis 
# =========================================================
def read_ground_motion(motion_txt):
    gm = [float(line.replace('\r','')) for line in motion_txt[:-1]]
    return gm

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

def response_calc(number_of_stories, haz_build, user_mass, seismicity, stories_height,
                 eq1, eq_dt, floor_height):
    #=================================================================
    # Start Calc
    #=================================================================
    wipe()
    maxNumIter = 150
    Tol = 1e-3
    if number_of_stories <=3:
        haz_type = 'l'
    elif number_of_stories >3 and number_of_stories<=7:
        haz_type = 'm'
    elif number_of_stories>7:
        print('hi')
        haz_type = 'h'
    # 
    buildingclass = {1: "w1",
                    2: "w2",
                    3: "s1",
                    4: "s2",
                    5: "s3",
                    6: "s4",
                    7: "s5",
                    8: "c1",
                    9: "c2",
                    10: "c3",
                    11: "pc1",
                    12: "pc2",
                    13: "rm1",
                    14: "rm2",
                    15: "urm"
                    }   
    building_hazus_final =  buildingclass[haz_build] + haz_type
    (hysteretic_paramp , hysteretic_paramn) = uniaxialCalc(building_hazus_final, seismicity , number_of_stories, user_mass)
    wipe()
    model('basic', '-ndm', 2, '-ndf', 2)
    for k in range(1, number_of_stories + 2):
        if k == 1:
            node(1, 0 , 0)
        else:
            node(k, *[0.0, stories_height[k-2]] , '-mass', *[user_mass[k-2], user_mass[k-2]])
    vals = [1, 1, 1]
    fix(1, *vals)
    # Get Data From DB
    # 
    print(hysteretic_paramn)
    pinching_data = PinchingData.objects.filter(building_type = haz_build)
    pinch_x = pinching_data[0].pinch_x
    pinch_y = pinching_data[0].pinch_y
    mat_beta = pinching_data[0].betta
    damp = pinching_data[0].damp
    print("pinch_x= ", pinch_x)
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
    tag1 = 1
    #==================================================================
    # Rayleigh Calculation
    #==================================================================
    if number_of_stories <= 3:
        n_eigen_j = number_of_stories * 2
    else:
        n_eigen_j = 6
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
    # Time Series
    #==================================================================
    g = 9.80665
    timeSeries('Path', tag1, '-dt', eq_dt, '-values', *eq1)
    pattern('UniformExcitation', tag1, 1, '-accel', tag1, '-factor', g)

    wipeAnalysis()
    constraints('Transformation')
    numberer('RCM')
    system('BandGeneral')

    tCurrent = 0.0
    test_dict = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 3:'EnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algorithm_dict = {1:'KrylovNewton', 2: 'SecantNewton' , 3:'ModifiedNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}
    tFinal = len(eq1) * eq_dt
    
    #==================================================================
    # Define Basic Dictionary to Catch Results
    #================================================================== 
    # Stories All Steps
    disp_each_story = {}
    vel_each_story = {}
    accel_each_story = {}
    drift_each_story = {}
    # 
    disp_each_story_max = []
    vel_each_story_max = []
    accel_modifier_each_story = {}
    accel_each_story_max = []
    drift_each_story_max = []
    for i in range(1, number_of_stories+2):
        disp_each_story[str(i)] = [0.0]
        vel_each_story[str(i)] = [0.0]
        accel_each_story[str(i)] = [0.0]
    for i in range(1, number_of_stories+1):
        drift_each_story['%d%d' %(i,i+1)] = [0.0]
    ok = 0
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
                    ok = analyze(1, eq_dt)
                    if ok == 0 :
                        tCurrent = tCurrent + eq_dt
                        for i in range(1,number_of_stories+2):
                            disp_each_story[str(i)].append(nodeDisp(i,1))
                            vel_each_story[str(i)].append(nodeVel(i,1))
                            accel_each_story[str(i)].append(nodeAccel(i,1))
                        for i in range(1,number_of_stories+1):
                            drift_each_story['%d%d' %(i,i+1)].append((nodeDisp(i+1,1) - nodeDisp(i,1)) / floor_height[i-1])
    for i in range(1,number_of_stories+2):
        disp_each_story_max.append(abs(max(disp_each_story[str(i)][:-1], key=abs)))
        vel_each_story_max.append(abs(max(vel_each_story[str(i)][:-1], key=abs)))
        # accel_each_story_max[str(i)] = accel_each_story[str(i)][:-1]
        # 
        # ========================================
        # accel generator
        # Here i create absolute acceleration !!!
        # ========================================
        rec_required = eq1
        rec_required.append(0)
        rec_required.insert(0, 0)
        # Absolute Acceleration
        accel_modifier_each_story[str(i)] = [ items1 / g + items2 for items1, items2 in zip(accel_each_story[str(i)][:-1], rec_required)]
        accel_each_story_max.append(abs(max(accel_modifier_each_story[str(i)][:-1], key=abs)))
    for i in range(1,number_of_stories+1):
        drift_each_story_max.append(abs(max(drift_each_story['%d%d' %(i,i+1)], key=abs)))
    wipe()
    return (disp_each_story_max, vel_each_story_max, accel_each_story_max, drift_each_story_max)

# Create your views here.
def main_project(request):
    return render(request, 'main.html')

def resp_estimate(request):
    # if request.POST or request.is_ajax():
    number_of_stories = int(request.POST.get('number_of_stories'))
    story_height = float(request.POST.get('stories_height'))
    building_type_hazus = int(request.POST.get('building_type_hazus'))
    stories_mass = request.POST.get('stories_mass')
    eq_dt = float(request.POST.get('eq_dt'))
    seismic_design_category = request.POST.get('seismic_design_category')
    seis_uni = {'0' : 'H', '1' : 'M', '2' : 'L', '3' : 'Pre'}
    seismicity = seis_uni[seismic_design_category] 
    # read ground motion data
    motion= request.FILES['motion'].read().decode("utf-8")
    data = motion.split('\n')
    eq1 = read_ground_motion(data)
    # ==========================================================
    # Data for Records
    rec_d_t = []
    for num in range(0, len(eq1)+1):
        rec_d_t.append(num * eq_dt)
    # Data for Spectrum
    periods = np.linspace(0.0, 4, 400)
    record = eqsig.AccSignal(eq1, eq_dt)   # define record in eqsig
    record.generate_response_spectrum(response_times=periods) # generate response spectrum
    spec = record.s_a


    # ==========================================================
    stories_height = []
    floor_height = []
    user_mass = []
    height = 0.0
    for i in range(1, int(number_of_stories) + 1):
        height += story_height
        stories_height.append(height)
        floor_height.append(story_height)
        user_mass.append(stories_mass)
    (disp_each_story_max, vel_each_story_max, accel_each_story_max, drift_each_story_max) = response_calc(number_of_stories, building_type_hazus, np.array(user_mass, dtype=np.float64), seismicity, 
                                                                                                          stories_height, eq1, eq_dt, floor_height)
    drift_each_story_max.insert(0, 0)
    response = {'disp_each_story_max' : disp_each_story_max,
                'vel_each_story_max' : vel_each_story_max, 
                'accel_each_story_max' : accel_each_story_max, 
                'drift_each_story_max' : drift_each_story_max,
                'periods' : periods.tolist(),
                'spec' : spec.tolist(),
                'eq': eq1,
                'rec_d_t': rec_d_t}
    return JsonResponse(response)
