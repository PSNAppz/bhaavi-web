from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def home(request):
    return render(request, 'base/main.html')

def  profile(request):
    return HttpResponse('profile')

def login(request):
    return render(request, 'accounts/login.html')    

def register(request):
    return render(request, 'accounts/register.html')    
        