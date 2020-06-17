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
    purchases = request.user.user_products.filter(status=1)
    schedules = request.user.schedule_times.none()
    user_requests = request.user.mentor_request.none()
    for purchase in purchases:
        if purchase.product_id == 2 or  purchase.product_id == 3:
            user_requests |= request.user.mentor_request.filter(product_id = purchase.product_id)
    #print("TYPE",requests)        
    for user_request in user_requests :
        if user_request.responded and not user_request.scheduled:
            schedules |= request.user.schedule_times.filter(request_id = user_request.id).filter(accepted = 0)
    context = {'call_request':None,'type':None, 'products':products, 'purchases':purchases, 'requests':user_requests , 'schedules':schedules}
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
    if request.method == "POST" :
        product_id = request.POST.get('product')
        user = request.user
        purchased_product = user.user_products.filter(status=1).get(product_id=product_id).product
        print(user, purchased_product)
        form = ScheduleRequestForm(request.POST)
        if form.is_valid():
            if str(purchased_product.id) == str(product_id):
                MentorCallRequest.objects.create(
                    user = user,
                    product = purchased_product
                ) 
    context = {'call_request':'success','type':'Mentor'}
    return redirect('dashboard')

