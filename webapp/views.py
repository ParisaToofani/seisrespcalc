from django.shortcuts import render, redirect

# Create your views here.
def main_project(request):
    return render(request, 'main.html')

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
    return
