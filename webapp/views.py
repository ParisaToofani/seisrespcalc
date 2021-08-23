from django.shortcuts import render, redirect

# Create your views here.
def main_project(request):
    return render(request, 'main.html')
