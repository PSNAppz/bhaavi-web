from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.db.models import DateField, Count
from django.db.models.functions import Cast
from django.contrib.auth import authenticate, login, logout
from decouple import config
from django.contrib.auth.decorators import login_required
from .decorators import *
from picset.models import Result
from .models import *
from .forms import *
from django.contrib import messages
import datetime
import pytz
import uuid
import hashlib
from .RtcTokenBuilder import buildToken
import razorpay
from collections import Counter

# from django.contrib.auth.tokens import default_token_generator
# from django.utils.encoding import force_bytes
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.template import loader
# from django.core.mail import send_mail
# from bhaavi.settings import EMAIL_HOST_USER
# from django.views.generic import FormView
# # from accounts.forms import PasswordResetRequestForm
# from django.contrib import messages
# from django.contrib.auth.models import User
# from django.db.models.query_utils import Q


from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .TokenBuilder import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage

utc= pytz.timezone('Asia/Kolkata')

def homePage(request):
    return render(request, 'base/home.html')

@login_required(login_url='login')
def profilePage(request):
    try:
        profile = UserProfile.objects.get(user_id = request.user.id)
        context = {'profile':profile}
    except Exception as e:    
        context = {'profile':None}

    return render(request, 'accounts/profile.html', context)

def plansPage(request):
    products = Product.objects.filter(active=True).filter(is_package=False)
    features = ProductFeatures.objects.all()
    packages = Product.objects.filter(active=True).filter(is_package=True)
    context = {'products':products, 'packages':packages, 'features':features}
    return render(request, 'accounts/plans.html', context)    

# Payment functions
@login_required(login_url='login')
def createOrder(request):
    if request.method == "POST":
        if not request.user.customer:
            messages.warning(request, 'You cannot purchase products!')
            return redirect('dashboard')
        product_id = request.POST.get('product')
        product = Product.objects.filter(active=True).get(pk=product_id)
        try:
            user_profile = UserProfile.objects.get(user_id = request.user.id)
        except UserProfile.DoesNotExist:
            user_profile = None
        if product:
            if product.is_package:
                products_in_package = ProductPackages.objects.filter(package_id = product.id)
                for pdt in products_in_package:
                    try:
                        check_product_status = UserPurchases.objects.filter(user_id = request.user.id).filter(product_id = pdt.product.id).get(status=True)
                        messages.warning(request, 'Product already purchased.')
                        return redirect('plans')
                    except UserPurchases.DoesNotExist:
                        pass
                try:
                    in_progress = UserPurchases.objects.filter(user_id = request.user.id).filter(payment_progress = True).get(product_id = product.id)
                    invoice = in_progress.invoice
                except UserPurchases.DoesNotExist:
                    purchase = UserPurchases.objects.create(
                        user = request.user,
                        product = product,
                        )
                    invoice = purchase.invoice 
                    for pdt in products_in_package:
                        purchase = UserPurchases.objects.create(
                            user = request.user,
                            product = pdt.product,
                            invoice = invoice,
                            )
                client = initPaymentClient()    
                order_amount = (product.amount - product.active_discount) * 100
                order_currency = 'INR'
                order_receipt = invoice
                notes = {'Product': product.name}   
                product_name = product.name
                response = client.order.create(dict(amount=order_amount, currency=order_currency, receipt=order_receipt, notes=notes, payment_capture='0'))
                order_id = response['id']
                order_status = response['status']
                if order_status=='created':
                    context = {'order_id':order_id, 'product':product, 'amount':order_amount,'profile':user_profile,'invoice':invoice}
                    return render(request, 'accounts/payment.html', context)
                else: 
                    messages.error(request, 'Some error occured, please try again!')
                    return redirect('plans')

            else:
                # Check if user already has the product
                try:
                    check_product_status = UserPurchases.objects.filter(user_id = request.user.id).filter(product_id = product.id).get(status=True)
                    messages.warning(request, 'Product already purchased.')
                    return redirect('plans')
                except UserPurchases.DoesNotExist:    
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
                    order_amount = (product.amount - product.active_discount) * 100
                    order_currency = 'INR'
                    order_receipt = invoice
                    notes = {'Product': product.name}   
                    product_name = product.name
                    response = client.order.create(dict(amount=order_amount, currency=order_currency, receipt=order_receipt, notes=notes, payment_capture='0'))
                    order_id = response['id']
                    order_status = response['status']
                    if order_status=='created':
                        context = {'order_id':order_id, 'product':product, 'amount':order_amount,'profile':user_profile,'invoice':invoice}
                        return render(request, 'accounts/payment.html', context)
                    else: 
                        messages.error(request, 'Some error occured, please try again!')
                        return redirect('plans')


@login_required(login_url='login')
def paymentSuccessPage(request):
    if request.method == "POST":
        response = request.POST
        try:
            response['razorpay_payment_id']
            razorpay_payment_id = response['razorpay_payment_id']
            razorpay_order_id = response['razorpay_order_id']
            razorpay_signature = response['razorpay_signature']
            status = paymentStatus(razorpay_payment_id, razorpay_order_id, razorpay_signature)
            if status:
                
                items = UserPurchases.objects.filter(invoice=response['invoice'])
                if not items.count() > 1:
                    purchase = UserPurchases.objects.get(invoice=response['invoice'])
                    user_id = purchase.user_id 
                    try:
                        check_saved =  RazorPayTransactions.objects.get(purchase_id=purchase.id)
                    except  RazorPayTransactions.DoesNotExist:
                        RazorPayTransactions.objects.create(
                            razorpay_payment_id = razorpay_payment_id,
                            razorpay_order_id = razorpay_order_id,
                            razorpay_signature = razorpay_signature,
                            status = 1,
                            purchase = purchase
                        )
                        UserPurchases.objects.filter(invoice=response['invoice']).update(payment_progress=0, status=1)
                else:
                    try:
                        check_saved =  RazorPayTransactions.objects.get(purchase_id=items[0].id)
                    except  RazorPayTransactions.DoesNotExist:
                        RazorPayTransactions.objects.create(
                            razorpay_payment_id = razorpay_payment_id,
                            razorpay_order_id = razorpay_order_id,
                            razorpay_signature = razorpay_signature,
                            status = 1,
                            purchase = items[0]
                        )
                        user_id = items[0].user_id 
                        for item in items:
                            if not item.product.is_package:
                                UserPurchases.objects.filter(pk = item.id).update(payment_progress=0, status=1)
                            else:
                                UserPurchases.objects.filter(pk = item.id).update(payment_progress=0)
                try:
                    user_profile = UserProfile.objects.get(user_id = user_id)
                    UserProfile.objects.filter(pk = user_profile.id).update(
                        mobile = response['mobile'],
                        address = response['address'],
                        state = response['state'],
                        pincode = response['pincode'],
                    )
                except UserProfile.DoesNotExist:
                    UserProfile.objects.create(
                        mobile = response['mobile'],
                        address = response['address'],
                        state = response['state'],
                        pincode = response['pincode'],
                        user = request.user
                    )        

                context = {'payment':True}
            else:
                context = {'payment':False}    
        except :
            context = {'payment':False}

        return render(request, 'accounts/success.html', context)           

# Conference call 
# check if scheduled in 30 min
@login_required(login_url='login')
def callDetails(request):
    # Token generation code
    def generateToken(uid, appID, appCertificate, channel, expiredTsInSeconds):
        token = buildToken(appID, appCertificate, channel, uid, expiredTsInSeconds)
        return token

    if request.method == "POST":
        schedule_id = request.POST.get('schedule')
        schedule = RequestedSchedules.objects.get(pk=schedule_id)
        
        if (schedule.accepted and schedule.user_id == request.user.id and schedule.request.scheduled and not schedule.request.closed):
            now = utc.localize(datetime.datetime.now())
            time_delta = (now - schedule.slot)
            total_seconds = time_delta.total_seconds()
            minutes = total_seconds/60
            if (minutes >= -5 and minutes <= 65): 
                accepted_call = AcceptedCallSchedule.objects.filter(schedule_id = schedule.id).get(completed=False)
                token = accepted_call.token
                if not token:
                    expiryTimeSec = 3600
                    appCert = config('AGORA_CERT_PRIMARY')
                    appID = config('AGORA_APP_ID')
                    uid = 0
                    channel = accepted_call.channel
                    token = generateToken(uid, appID, appCert, channel, expiryTimeSec )
                    AcceptedCallSchedule.objects.filter(schedule_id = schedule.id).filter(completed=False).update(token=token)
                context = {'minutes':minutes,'scheduled':True, 'schedule':schedule.id}
                return render(request, 'accounts/pre_call_user.html', context)
            else:
                if (minutes < -5):
                    context = {'minutes':minutes,'scheduled':False}
                    return render(request, 'accounts/pre_call_user.html', context)
                else:
                    context = {'minutes':minutes,'scheduled':False}
                    return render(request, 'accounts/pre_call_user.html', context)
        else:
            try:
                profile = MentorProfile.objects.get(user_id = request.user.id)
            except MentorProfile.DoesNotExist:
                return redirect('home')    
            if (schedule.accepted and schedule.mentor_id == profile.id and schedule.request.scheduled and not schedule.request.closed):
                now = utc.localize(datetime.datetime.now())
                time_delta = (now - schedule.slot)
                total_seconds = time_delta.total_seconds()
                minutes = total_seconds/60
                if (minutes >= -5 and minutes <= 65):
                    accepted_call = AcceptedCallSchedule.objects.filter(schedule_id = schedule.id).get(completed=False)
                    token = accepted_call.token
                    if not token:
                        expiryTimeSec = 3600
                        appCert = config('AGORA_CERT_PRIMARY')
                        appID = config('AGORA_APP_ID')
                        uid = 0
                        channel = accepted_call.channel
                        token = generateToken(uid, appID, appCert, channel, expiryTimeSec )
                        AcceptedCallSchedule.objects.filter(schedule_id = schedule.id).filter(completed=False).update(token=token)
                    context = {'minutes':minutes,'scheduled':True,'schedule':schedule.id}
                    return render(request, 'accounts/pre_call_mentor.html', context)
                else:
                    if (minutes < -5):
                        context = {'minutes':minutes,'scheduled':False}
                        return render(request, 'accounts/pre_call_mentor.html', context)
                    else:
                        context = {'minutes':minutes,'scheduled':False}
                        return render(request, 'accounts/pre_call_mentor.html', context)
            return redirect('mentorboard')

                
@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password =request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.warning(request, 'Email or password incorrect')

    return render(request, 'accounts/login.html')   

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

            # email_verification..........
            user.is_active=False
            current_site = get_current_site(request)
            email_subject = 'Activate Your Account'
            message = render_to_string('email_verification.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(email_subject, message, to=[to_email])
            email.send()
            # return HttpResponse('We have sent you an email, please confirm your email address to complete registration')

            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Succesfully registered!')
                return redirect('profile')

        else:
            messages.warning(request, "The password must contain 6 characters with at least one letter and at least one digit or punctuation character.")
        

    context = {'form':form,'type':'User'}
    return render(request, 'accounts/register.html', context)     
# email verification.
def activate_account(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse('Your account has been activate successfully')
    else:
        return HttpResponse('Activation link is invalid!')

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
        dob = request.POST.get('dob')
        institute = request.POST.get('institute')
        gender = request.POST.get('gender')
        siblings = request.POST.get('siblings')
        language = request.POST.get('language')
        contact = int(request.POST.get('contact'))  
        hobbies = request.POST.get('hobbies')
        address = request.POST.get('address')
        guardian_name = request.POST.get('guardian')
        career_concerns = request.POST.getlist('career')
        personal_concerns = request.POST.getlist('personal')
        suggested_date = request.POST.get('suggested_slot')  
        suggested_time = request.POST.get('period')  
        career_conc = []
        personal_conc = []
        for career_ in career_concerns:
            if career_ == "1":
                career_concerns.append("Course / Higher Education")
            elif career_ == "2":
                career_concerns.append("Career / Job Related")
            elif career_ == "3":
                career_concerns.append("Formulation of Study/ Academic Plans")
            else:
                career_concerns.append("Other")     

        for personal_ in personal_concerns:
            if personal_ == "1":
                personal_conc.append("Interpersonal Issues")
            elif personal_ == "2":
                personal_conc.append("Family Problems")
            elif personal_ == "3":
                personal_conc.append("Medical & Health Related")
            else:
                personal_conc.append("Other")                   

        if gender == "1":
            gender = "Male"
        elif gender == "2":
            gender = "Female"  
        else:
            gender = "N/A" 

        if suggested_time == "1":
            suggested_time = "First half"
        elif suggested_time == "2":
            suggested_time = "Second half"  
        else:
            suggested_time = "No preference" 

        if (product_id == None or user == None or dob == None or institute == None or gender == None or siblings == None or language == None or contact ==  None or hobbies == None or guardian_name == None or career_concern ==  None or personal_concern == None or suggested_date == None or suggested_time == None ):
            messages.warning(request, 'Please fill all the required fields!')
            return redirect('dashboard')  

        try:
            pending = MentorCallRequest.objects.filter(user_id = user.id).filter(product_id = product_id).get(closed=False)
            messages.warning(request, 'Call already Requested')
            return redirect('dashboard')
        except MentorCallRequest.DoesNotExist:
            purchased_product = user.user_products.filter(status=1).get(product_id=product_id).product
            if str(purchased_product.id) == str(product_id) and purchased_product.call_required:

                MentorCallRequest.objects.create(
                    user = user,
                    product = purchased_product,
                    language = request.POST.get('language'),
                    request_date = request.POST.get('suggested_slot'),  
                    requested_slot = suggested_time  
                ) 
                try:
                    profile = UserProfile.objects.get(user_id = user.id)
                    UserProfile.objects.filter(user_id = user.id).update(
                        gender = gender,
                        siblings = request.POST.get('siblings'),
                        mobile = contact,  
                        hobbies = request.POST.get('hobbies'),
                        guardian_name = request.POST.get('guardian'),
                        career_concern =  career_conc,
                        personal_concern =  personal_conc,
                        dob = request.POST.get('dob'),
                        institute = request.POST.get('institute'),
                        address = request.POST.get('address')
                    )
                except Exception as e:
                    UserProfile.objects.create(
                        user_id = user.id,
                        gender = gender,
                        siblings = request.POST.get('siblings'),
                        mobile = contact,  
                        hobbies = request.POST.get('hobbies'),
                        guardian_name = request.POST.get('guardian'),
                        career_concern =  career_conc,
                        personal_concern =  personal_conc,
                        dob = request.POST.get('dob'),
                        address = request.POST.get('address'),
                        institute = request.POST.get('institute')
                    )
                    print(e)
                messages.success(request, 'Call Schedule requested succesfully. Please wait for admin to respond!')
            else:
                messages.error(request, 'An error occured!')


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
            if ((schedule.user_id == request.user.id or request.user.is_superuser) and not call_request.scheduled):
                AcceptedCallSchedule.objects.create(
                    schedule = schedule
                )
                RequestedSchedules.objects.filter(pk=schedule_id).update(accepted=True) 
                MentorCallRequest.objects.filter(pk=call_request_id).update(scheduled=True)
                messages.success(request, 'Call Scheduled!')
            else:
                messages.error(request, 'Schedule invalid!')


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
        clash_requests_user = MentorCallRequest.objects.filter(user_id = user_id).filter(closed=0).filter(responded=1).exclude(product_id = product_id)
        mentor_schedules = RequestedSchedules.objects.filter(mentor_id = mentor.id)
        if form.is_valid():
            for mentor_schedule in mentor_schedules:
                clash_request_mentor = MentorCallRequest.objects.get(pk = mentor_schedule.request_id)
                print(clash_request_mentor)
                if not clash_request_mentor.closed:
                    time_delta = (mentor_schedule.slot - slot)
                    total_seconds = time_delta.total_seconds()
                    minutes = total_seconds/60
                    if (minutes <= 120 and minutes >= -120):
                        messages.warning(request, 'Mentor Schedule clash found, please add a different time for the new schedule.')
                        return redirect('admin_panel')

            if clash_requests_user:
                for clash in clash_requests_user:
                    check_clashes = RequestedSchedules.objects.filter(request_id = clash.id)
                    for clash_req in check_clashes:
                        time_delta = (clash_req.slot - slot)
                        total_seconds = time_delta.total_seconds()
                        minutes = total_seconds/60
                        if (minutes <= 120 and minutes >= -120):
                            messages.warning(request, 'User Schedule clash found, please add a different time for the new schedule.')
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
                                messages.success(request, 'Schedule added succesfully!')
                                return redirect('admin_panel')  
                            else:
                                for schedules in check_schedules:
                                    time_delta = (schedules.slot - slot)
                                    total_seconds = time_delta.total_seconds()
                                    minutes = total_seconds/60
                                    if (minutes <= 5 and minutes >= -5):
                                        messages.warning(request, 'Schedule within 5 min already exist!')
                                        return redirect('admin_panel') 
                                    else:
                                        RequestedSchedules.objects.create(
                                            user = user,
                                            mentor = mentor,
                                            request = call_request,
                                            slot = slot
                                        )
                                        MentorCallRequest.objects.filter(pk=request_id).update(responded=True) 
                                        messages.success(request, 'Schedule added succesfully!')
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
                    messages.success(request, 'Schedule added succesfully!')
                    return redirect('admin_panel')  
                else:
                    for schedules in check_schedules:
                        time_delta = (schedules.slot - slot)
                        total_seconds = time_delta.total_seconds()
                        minutes = total_seconds/60
                        if (minutes <= 5 and minutes >= -5):
                            messages.warning(request, 'Schedule within 5 min already exist!')
                            return redirect('admin_panel')  
                        else:
                            RequestedSchedules.objects.create(
                                user = user,
                                mentor = mentor,
                                request = call_request,
                                slot = slot
                            )
                            MentorCallRequest.objects.filter(pk=request_id).update(responded=True)
                            messages.success(request, 'Schedule added succesfully!')
                            return redirect('admin_panel')  

    return redirect('admin_panel')   

@login_required(login_url='login')
def userDashboard(request):
    if not request.user.customer:
        if  request.user.is_jyolsyan:
            return redirect('mentorboard') #TODO: Dashboard for Jyolsyan
        if  request.user.is_mentor:
            return redirect('mentorboard')
        if  request.user.is_superuser:       
            return redirect('admin_panel')

    products = Product.objects.filter(is_package=0).filter(active=1)
    purchases = request.user.user_products.filter(status=1)
    schedules = request.user.schedule_times.none()
    user_requests = request.user.mentor_request.none()
    accepted_calls = AcceptedCallSchedule.objects.none()
    results = Result.objects.filter(user_id = request.user.id).order_by('id')
    
    for purchase in purchases:
        if purchase.product.call_required:
            user_requests |= request.user.mentor_request.filter(product_id = purchase.product_id)
    for user_request in user_requests :
        if user_request.responded and not user_request.scheduled:
            schedules |= request.user.schedule_times.filter(request_id = user_request.id).filter(accepted = 0)
        elif user_request.responded and user_request.scheduled and not user_request.closed:
            schedule = RequestedSchedules.objects.filter(request_id = user_request.id).get(accepted=True)
            accepted_calls |= AcceptedCallSchedule.objects.filter(schedule_id = schedule.id)
        else:
            pass    
    context = {'products':products, 'purchases':purchases, 'requests':user_requests , 'schedules':schedules, 'accepted_calls':accepted_calls,'results':results}
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
            messages.success(request, 'Schedule deleted succesfully!')
    return redirect('admin_panel') 

@login_required(login_url='login')
@admin_user
def respondCallRequest(request, id):
    try:
        call_request = MentorCallRequest.objects.get(pk=id)
        user = call_request.user
        mentor_products = MentorProducts.objects.filter(product_id = call_request.product.id)
        mentors = MentorProfile.objects.none()
    
        for mentor in mentor_products:
            mentors |= MentorProfile.objects.filter(pk = mentor.mentor_id)
        context = {'request':call_request,'request_user':user,'mentors':mentors}
    except MentorCallRequest.DoesNotExist:
        raise Http404("Request does not exist")
    return render(request, 'admin/call_view.html',context) 

def initPaymentClient():
    rpay_id = config('RazorPay_ID')
    rpay_seceret = config('RazorPay_Secret')
    client = razorpay.Client(auth=(rpay_id, rpay_seceret))
    return client

def paymentStatus(razorpay_payment_id, razorpay_order_id,  razorpay_signature):
    params_dict = {
        'razorpay_payment_id' : razorpay_payment_id,
        'razorpay_order_id' : razorpay_order_id,
        'razorpay_signature' : razorpay_signature
    }
    # VERIFYING SIGNATURE
    try:
        client = initPaymentClient()    
        client.utility.verify_payment_signature(params_dict)
        return True
    except Exception as e:
        return False
     
@login_required(login_url='login')
@mentor
def mentorDashboard(request):
    profile = MentorProfile.objects.get(user_id = request.user.id)
    schedules = RequestedSchedules.objects.filter(mentor_id = profile.id).filter(accepted=True)
    context = {'schedules':schedules, 'profile':profile}
    return render(request, 'mentor/dashboard.html',context)

def saveProfile(request):
    try:
        mob = int(request.POST.get('mobile'))
        address = request.POST.get('address')
        state = request.POST.get('state')
        pincode = int(request.POST.get('pincode'))

        if ( (len(str(mob)) < 10 or len(str(mob)) > 10) or len(address) == 0  or len(state) == 0 or not (len(str(pincode)) == 6 )):
            messages.error(request, 'Please fill all the mandatory fields!')
            return redirect('profile') 

        qualification = request.POST.get('qualification')
        stream = request.POST.get('stream')
        institute = request.POST.get('institute')
        mark = request.POST.get('mark')
    except Exception as e:
        print(e)
        messages.error(request, 'Invalid data, please enter valid data')
        return redirect('profile')    
    try:
        user_profile = UserProfile.objects.get(user_id = request.user.id)
        UserProfile.objects.filter(pk = user_profile.id).update(
            mobile = mob,
            address = address,
            state = state,
            pincode = pincode,
            qualification = qualification,
            stream = stream,
            institute = institute,
            mark = mark
        )
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(
            mobile = mob,
            address = address,
            state = state,
            pincode = pincode,
            user = request.user,
            qualification = qualification,
            stream = stream,
            institute = institute,
            mark = mark
        )            
    return redirect('dashboard')

def requestPage(request):
    slots= []
    kv = {}
    time_slots = []
    daily_sessions = int(config('Daily_Call_Sessions'))
    if request.method == "POST" :
        product_id = request.POST.get('product')
        user = request.user
        schedules = RequestedSchedules.objects.none()
        accepted_requests = MentorCallRequest.objects.none()
        product = Product.objects.get(pk=product_id)
        related_prods = Product.objects.filter(prod_type=product.prod_type)

        for product in related_prods:
            accepted_requests |= MentorCallRequest.objects.filter(product_id = product.id).filter(scheduled=True).filter(closed=False)
        for a_request in accepted_requests:
            schedules |= RequestedSchedules.objects.filter(request_id=a_request.id).filter(accepted=True)

        for schedule in schedules:
            now = schedule.slot                
            kv.update({now:now.strftime("%d-%m-%Y")+",No slots available"})

        results = Counter(kv.values())
        for result in results:
            if results[result] >= daily_sessions:
                slots.append(result)
    UserProfile.objects.filter(user_id = user.id)
    context = {'slots':slots, 'product':product.id}
    return render(request, 'accounts/request.html',context)    

def viewPrivacyPolicy(request):
    return render(request, 'base/privacy.html')

def viewTerms(request):
    return render(request, 'base/terms.html')

def viewRefund(request):
    return render(request, 'base/refund.html')

# ERROR HANDLING..
def handler404(request, exception):
    context = {}
    response = render(request, "errors/404.html", context=context)
    response.status_code = 404
    return response

def handler500(request,exception=None):
    context = {}
    response = render(request, "errors/500.html", context=context)
    response.status_code = 500
    return response

def handler403(request,exception=None):
    context = {}
    response = render(request, "errors/403.html", context=context)
    response.status_code = 403
    return response

def handler400(request,exception=None):
    context = {}
    response = render(request, "errors/400.html", context=context)
    response.status_code = 400
    return response

# Password Reset

# class ResetPasswordRequestView(FormView):
#     template_name = "accounts/password_reset.html"
#     success_url = '/accounts/login'
#     form_class = PasswordResetRequestForm

#     def form_valid(self, *args, **kwargs):
#         form = super(ResetPasswordRequestView, self).form_valid(*args, **kwargs)
#         data= form.cleaned_data["email_or_username"]
#         user= User.objects.filter(Q(email=data)|Q(full_name=data)).first()
#         if user:
#             c = {
#                 'email': user.email,
#                 'domain': self.request.META['HTTP_HOST'],
#                 'site_name': 'Bhaavi.in',
#                 'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#                 'user': user,
#                 'token': default_token_generator.make_token(user),
#                 'protocol': self.request.scheme,
#             }
#             email_template_name='accounts/password_reset_email.html'
#             subject = "Reset Your Password"
#             email = loader.render_to_string(email_template_name, c)
#             send_mail(subject, email, EMAIL_HOST_USER , [user.email], fail_silently=False)
#         messages.success(self.request, 'An email has been sent to ' + data +" if it is a valid user.")
#         return form