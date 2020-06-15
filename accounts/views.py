from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
# Create your views here.
from django.contrib.auth.decorators import login_required
from .decorators import *
from .models import *
from .forms import *
from django.contrib import messages


def homePage(request):
    return render(request, 'base/home.html')

@login_required(login_url='login')
def userDashboard(request):
    products = Product.objects.all()
    purchases = request.user.user_products.all()
    requests = request.user.mentor_request.all()
    context = {'request':'success', 'products':products, 'purchases':purchases, 'requests':requests}
    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='login')
@admin_user
def adminDashboard(request):
    return render(request, 'accounts/adminpanel.html')    

@login_required(login_url='login')
def profilePage(request):
    return render(request, 'accounts/profile.html')

@login_required(login_url='login')
def plansPage(request):
    return render(request, 'accounts/plans.html')    

@login_required(login_url='login')
def checkoutPage(request):
    return render(request, 'accounts/checkout.html')        

@login_required(login_url='login')
def paymentSuccessPage(request):
    return render(request, 'accounts/success.html')        

def pricingDetails(request):
    return render(request, 'base/pricing.html')    

def chatpage(requset):
    return render(requset, 'accounts/video.html')


@unauthenticated_user
def loginPage(request):
    messages =''
    if request.method == 'POST':
        email = request.POST.get('email')
        password =request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages ='Email or password incorrect'

    context = {'form':messages}
    return render(request, 'accounts/login.html', context)   

def logoutUser(request):
    logout(request)
    return redirect('login') 
    
@unauthenticated_user
def userRegisterPage(request):
    form = RegisterUserForm()
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('full_name')

            email = request.POST.get('email')
            password =request.POST.get('password1')
        
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')

    context = {'form':form,'type':'User'}
    return render(request, 'accounts/register.html', context)     

@unauthenticated_user
def mentorRegisterPage(request):
    form = RegisterMentorForm()
    if request.method == 'POST':
        form = RegisterMentorForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('full_name')

            return redirect('login')
        

    context = {'form':form,'type':'Mentor'}
    return render(request, 'accounts/register.html', context)   
        
@unauthenticated_user
def jyolsyanRegisterPage(request):
    form = RegisterJyolsyanForm()
    if request.method == 'POST':
        form = RegisterJyolsyanForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('full_name')
            return redirect('login')
        

    context = {'form':form,'type':'Jyolsyan'}
    return render(request, 'accounts/register.html', context)   


 ## Request system
@login_required(login_url='login')
def requestSchedule(request):
    form = ScheduleRequestForm()
    if request.method == "POST" :
        form = ScheduleRequestForm(request.POST)
        print(form.data.get('user'))
        if form.is_valid():
            user_id = form.data.get('user')
            user = User.objects.get(id=user_id)
            # if user.user_products:
            print(user.user_products.get(id=2).product.name)
            print(user.mentor_request.count())
    context = {'request':'success','type':'Mentor'}
    return redirect('dashboard')

