from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
# Create your views here.
from django.contrib.auth.decorators import login_required
from .decorators import *
from .models import *
from .forms import *
from django.contrib import messages
import datetime


def homePage(request):
    return render(request, 'base/home.html')

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
def requestCall(request):
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

@login_required(login_url='login')
@admin_user
def requestSchedule(request):
    if request.method == "POST" :
        mentor_id = request.POST.get('mentor')
        user_id = request.POST.get('user')
        request_id = request.POST.get('request')
        dt = request.POST.get('slot')
        slot = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M")
        user = User.objects.get(pk=user_id)
        call_request = MentorCallRequest.objects.get(pk=request_id)
        mentor = MentorProfile.objects.get(pk=mentor_id)
        form = RequestedSchedulesForm(request.POST)
        check_schedules = RequestedSchedules.objects.filter(request_id = request_id).filter(mentor_id= mentor_id)
        if form.is_valid():
            if not check_schedules:
                RequestedSchedules.objects.create(
                    user = user,
                    mentor = mentor,
                    request = call_request,
                    slot = slot
                )
                MentorCallRequest.objects.filter(pk=request_id).update(responded=True)
            #else: # TODO: Add method here
                #Already scheduled with same request and mentor
    return redirect('admin_panel')   

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
    context = {'products':products, 'purchases':purchases, 'requests':user_requests , 'schedules':schedules}
    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='login')
@admin_user
def adminDashboard(request):
    call_requests = MentorCallRequest.objects.all().order_by('-responded')
    context = {'requests':call_requests}
    return render(request, 'admin/adminpanel.html', context)   

@login_required(login_url='login')
@admin_user
def respondCallRequest(request, id):
    try:
        call_request = MentorCallRequest.objects.get(pk=id)
        user = call_request.user
        mentor_type = 'C' if call_request.product.id == 2 else 'J' 
        mentors = MentorProfile.objects.filter(mentor_type = mentor_type)
        print(mentors)
        context = {'request':call_request,'request_user':user,'mentors':mentors}
    except MentorCallRequest.DoesNotExist:
        raise Http404("Request does not exist")
    return render(request, 'admin/call_view.html',context)     

