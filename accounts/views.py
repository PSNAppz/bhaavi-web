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
import pytz
import uuid
import razorpay
from decouple import config

utc=pytz.UTC

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
    if request.method == "POST":
        product_id = request.POST.get('product')
        product = Product.objects.filter(active=True).get(pk=product_id)
        if product:
            name = request.user.full_name
            email = request.user
            context = {'product':product,'name':name,'email':email}
            return render(request, 'accounts/checkout.html',context)
        # else: TODO: Return error            

@login_required(login_url='login')
def paymentSuccessPage(request):
    if request.method == "POST":
        response = request.POST
        if response['razorpay_payment_id']:
            razorpay_payment_id = response['razorpay_payment_id']
            razorpay_order_id = response['razorpay_order_id']
            razorpay_signature = response['razorpay_signature']
            status = paymentStatus(razorpay_payment_id, razorpay_order_id, razorpay_signature)
            if status:
                purchase = UserPurchases.objects.get(invoice=response['invoice'])
                RazorPayTransactions.objects.create(
                    razorpay_payment_id = razorpay_payment_id,
                    razorpay_order_id = razorpay_order_id,
                    razorpay_signature = razorpay_signature,
                    status = 1,
                    purchase = purchase
                )
                UserPurchases.objects.filter(invoice=response['invoice']).update(payment_progress=0, status=1)
            context = {'payment':True}
        else:
            context = {'payment':False}

        return render(request, 'accounts/success.html', context)        

def pricingDetails(request):
    return render(request, 'base/pricing.html')    

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
        form = ScheduleRequestForm(request.POST)
        if form.is_valid():
            if str(purchased_product.id) == str(product_id):
                MentorCallRequest.objects.create(
                    user = user,
                    product = purchased_product
                ) 
    #TODO: Send success message
    return redirect('dashboard')

@login_required(login_url='login')
def acceptCall(request):
    if request.method == "POST" :
        schedule_id = request.POST.get('schedule')
        schedule = RequestedSchedules.objects.get(pk=schedule_id) 
        call_request_id = schedule.request.id
        call_request =  MentorCallRequest.objects.get(pk=call_request_id)
        form = AcceptedSchedulesForm(request.POST)
        if form.is_valid():
            if schedule.user_id == request.user.id and not call_request.scheduled:
                AcceptedCallSchedule.objects.create(
                    schedule = schedule
                )
                RequestedSchedules.objects.filter(pk=schedule_id).update(accepted=True) 
                MentorCallRequest.objects.filter(pk=call_request_id).update(scheduled=True)
                # TODO: Success message
            else:
                # TODO: schedule invalid message
                print("Invalid schedule")     

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
        slot = utc.localize(slot)
        user = User.objects.get(pk=user_id)
        call_request = MentorCallRequest.objects.get(pk=request_id)
        mentor = MentorProfile.objects.get(pk=mentor_id)
        product_id = call_request.product_id 
        form = RequestedSchedulesForm(request.POST)
        check_schedules = RequestedSchedules.objects.filter(request_id = request_id)
        clash_requests = MentorCallRequest.objects.filter(user_id = user_id).filter(closed=0).filter(responded=1).exclude(product_id = product_id)
        if form.is_valid():
            if clash_requests:
                for clash in clash_requests:
                    check_clashes = RequestedSchedules.objects.filter(request_id = clash.id)
                    for clash_req in check_clashes:
                        time_delta = (clash_req.slot - slot)
                        total_seconds = time_delta.total_seconds()
                        minutes = total_seconds/60
                        if (minutes <= 120 and minutes >= -120):
                            # TODO: Show error message
                            print(minutes,"TODO: Schedule clashing")
                            return redirect('admin_panel')
                        else:
                            if not check_schedules:
                                RequestedSchedules.objects.create(
                                    user = user,
                                    mentor = mentor,
                                    request = call_request,
                                    slot = slot
                                )
                                print("Schedule added")
                                MentorCallRequest.objects.filter(pk=request_id).update(responded=True)
                                return redirect('admin_panel')  
                            else:
                                for schedules in check_schedules:
                                    time_delta = (schedules.slot - slot)
                                    total_seconds = time_delta.total_seconds()
                                    minutes = total_seconds/60
                                    if (minutes <= 5 and minutes >= -5):
                                        # TODO: Show error message
                                        print(minutes,"TODO: Schedule within 5 min already exist")
                                        return redirect('admin_panel') 
                                    else:
                                        RequestedSchedules.objects.create(
                                            user = user,
                                            mentor = mentor,
                                            request = call_request,
                                            slot = slot
                                        )
                                        print("Schedule added")
                                        MentorCallRequest.objects.filter(pk=request_id).update(responded=True) 
                                        return redirect('admin_panel')  
            else:    
                if not check_schedules:
                    RequestedSchedules.objects.create(
                        user = user,
                        mentor = mentor,
                        request = call_request,
                        slot = slot
                    )
                    MentorCallRequest.objects.filter(pk=request_id).update(responded=True)
                    return redirect('admin_panel')  
                else:
                    for schedules in check_schedules:
                        time_delta = (schedules.slot - slot)
                        total_seconds = time_delta.total_seconds()
                        minutes = total_seconds/60
                        if (minutes <= 5 and minutes >= -5):
                            # TODO: Show error message
                            print(minutes,"TODO: Schedule within 5 min already exist")
                            return redirect('admin_panel')  
                        else:
                            RequestedSchedules.objects.create(
                                user = user,
                                mentor = mentor,
                                request = call_request,
                                slot = slot
                            )
                            MentorCallRequest.objects.filter(pk=request_id).update(responded=True)
                            return redirect('admin_panel')  

    return redirect('admin_panel')   

@login_required(login_url='login')
def userDashboard(request):
    products = Product.objects.filter(active=1)
    purchases = request.user.user_products.filter(status=1)
    schedules = request.user.schedule_times.none()
    user_requests = request.user.mentor_request.none()
    accepted_calls = AcceptedCallSchedule.objects.none()
    
    for purchase in purchases:
        if purchase.product.call_required:
            user_requests |= request.user.mentor_request.filter(product_id = purchase.product_id)
    #print("TYPE",requests)        
    for user_request in user_requests :
        if user_request.responded and not user_request.scheduled:
            schedules |= request.user.schedule_times.filter(request_id = user_request.id).filter(accepted = 0)
        elif user_request.responded and user_request.scheduled and not user_request.closed:
            schedule = RequestedSchedules.objects.filter(request_id = user_request.id).get(accepted=True)
            accepted_calls |= AcceptedCallSchedule.objects.filter(schedule_id = schedule.id)
        else:
            pass    
    context = {'products':products, 'purchases':purchases, 'requests':user_requests , 'schedules':schedules, 'accepted_calls':accepted_calls}
    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='login')
@admin_user
def adminDashboard(request):
    call_requests = MentorCallRequest.objects.all().order_by('-responded')
    context = {'requests':call_requests}
    return render(request, 'admin/adminpanel.html', context)   

@login_required(login_url='login')
@admin_user
def showSchedules(request, id):
    schedules = RequestedSchedules.objects.filter(request_id=id)
    user = User.objects.get(pk=schedules[0].user_id)
    context = {'schedules':schedules,'requested_user':user}
    return render(request, 'admin/view_schedule.html', context) 

@login_required(login_url='login')
@admin_user
def dropSchedule(request, id):
    if request.method == "POST":
        schedule = RequestedSchedules.objects.get(pk=id)
        request_id = schedule.request.id
        all_requests = RequestedSchedules.objects.filter(request_id = request_id)
        if (all_requests.count()>1):
            schedule.delete()
        else:
            MentorCallRequest.objects.filter(pk=schedule.request.id).update(responded = False)
            schedule.delete()
    return redirect('admin_panel') 

@login_required(login_url='login')
@admin_user
def respondCallRequest(request, id):
    try:
        call_request = MentorCallRequest.objects.get(pk=id)
        user = call_request.user
        mentors = MentorProfile.objects.filter(associated_product_id = call_request.product.id)
        context = {'request':call_request,'request_user':user,'mentors':mentors}
    except MentorCallRequest.DoesNotExist:
        raise Http404("Request does not exist")
    return render(request, 'admin/call_view.html',context) 

def initPaymentClient():
    rpay_id = config('RazorPay_ID')
    rpay_seceret = config('RazorPay_Secret')
    client = razorpay.Client(auth=(rpay_id, rpay_seceret))
    return client

# Payment URLs TODO: Secure these links
@login_required(login_url='login')
def createOrder(request):
    if request.method == "POST":
        product_id = request.POST.get('product')
        product = Product.objects.filter(active=True).get(pk=product_id)
        if product:
            try:
                in_progress = UserPurchases.objects.filter(user_id = request.user.id).filter(payment_progress = True).get(product_id = product.id)
                invoice = in_progress.invoice
            except UserPurchases.DoesNotExist:
                purchase = UserPurchases.objects.create(
                                    user = request.user,
                                    product = product,
                            )
                invoice = purchase.invoice             
            client = initPaymentClient()    
            order_amount = product.amount * 100
            order_currency = 'INR'
            order_receipt = 'order_rcptid_11'
            notes = {'Product': product.name}   
            product_name = product.name
            name = request.user.full_name
            email = request.user
            response = client.order.create(dict(amount=order_amount, currency=order_currency, receipt=order_receipt, notes=notes, payment_capture='0'))
            order_id = response['id']
            order_status = response['status']
            if order_status=='created':
                print(invoice)
                context = {'order_id':order_id, 'product':product_name, 'amount':order_amount,'name':name,'email':email,'invoice':invoice}
                return render(request, 'accounts/payment.html', context)
            # else: TODO: Return error    

def paymentStatus(razorpay_payment_id, razorpay_order_id,  razorpay_signature):
    params_dict = {
        'razorpay_payment_id' : razorpay_payment_id,
        'razorpay_order_id' : razorpay_order_id,
        'razorpay_signature' : razorpay_signature
    }
    # VERIFYING SIGNATURE
    client = initPaymentClient()    
    status = client.utility.verify_payment_signature(params_dict)
    return True
     

