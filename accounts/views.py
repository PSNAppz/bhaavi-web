from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
# Create your views here.
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import CreateUserForm
from django.contrib import messages

@login_required(login_url='login')
def homePage(request):
    return render(request, 'base/main.html')


def  profilePage(request):
    return HttpResponse('profile')

def loginPage(request):
    if request.user.is_authenticated:
	    return redirect('home')
    else:
	    if request.method == 'POST':
		    username = request.POST.get('username')
		    password =request.POST.get('password')

		    user = authenticate(request, username=username, password=password)

		    if user is not None:
			    login(request, user)
			    return redirect('home')
		    else:
			    messages.info(request, 'Username OR password is incorrect')

	    context = {}
	    return render(request, 'accounts/login.html', context)   

def logoutUser(request):
    logout(request)
    return redirect('login') 
    
def registerPage(request):
	if request.user.is_authenticated:
	    return redirect('home')
	else:
		form = CreateUserForm()
		if request.method == 'POST':
			form = CreateUserForm(request.POST)
			if form.is_valid():
				form.save()
				user = form.cleaned_data.get('username')
				messages.success(request, 'Account was created for ' + user)

				return redirect('login')
			

		context = {'form':form}
		return render(request, 'accounts/register.html', context)        