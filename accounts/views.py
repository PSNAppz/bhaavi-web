from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from decouple import config
from django.contrib.auth.decorators import login_required

from schedule.models import FinalMentorReport, AssignSubmitReport, AstrologerCareerReport
from .decorators import *
from picset.models import Result
from .forms import *
from django.contrib import messages
import datetime
import pytz
from .RtcTokenBuilder import buildToken
import razorpay
from collections import Counter

from .models import *
from product.models import *
from mentor.models import *
from payment.models import *

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
from django.core.mail import EmailMessage

utc = pytz.timezone('Asia/Kolkata')
seconds = 60
expiryTimeSec = 5600
number = -5
number2 = 65
number3 = 5


def homePage(request):
    return render(request, 'base/home.html')


@login_required(login_url='login')
def profilePage(request):
    try:
        profile = UserProfile.objects.get(user_id=request.user.id)
        context = {'profile': profile}
    except Exception as e:
        context = {'profile': None}

    return render(request, 'accounts/profile.html', context)


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

        if (
                schedule.accepted and schedule.user_id == request.user.id and schedule.request.scheduled and not schedule.request.closed):
            now = utc.localize(datetime.datetime.now())
            time_delta = (now - schedule.slot)
            total_seconds = time_delta.total_seconds()
            minutes = total_seconds / seconds
            if (minutes >= number and minutes <= number2):
                accepted_call = AcceptedCallSchedule.objects.filter(schedule_id=schedule.id).get(completed=False)
                token = accepted_call.token
                if not token:
                    appCert = config('AGORA_CERT_PRIMARY')
                    appID = config('AGORA_APP_ID')
                    uid = 0
                    channel = accepted_call.channel
                    token = generateToken(uid, appID, appCert, channel, expiryTimeSec)
                    AcceptedCallSchedule.objects.filter(schedule_id=schedule.id).filter(completed=False).update(
                        token=token)
                context = {'minutes': minutes, 'scheduled': True, 'schedule': schedule.id}
                return render(request, 'accounts/pre_call_user.html', context)
            else:
                if (minutes < number):
                    context = {'minutes': minutes, 'scheduled': False}
                    return render(request, 'accounts/pre_call_user.html', context)
                else:
                    context = {'minutes': minutes, 'scheduled': False}
                    return render(request, 'accounts/pre_call_user.html', context)
        else:
            try:
                profile = MentorProfile.objects.get(user_id=request.user.id)
            except MentorProfile.DoesNotExist:
                return redirect('home')
            if (
                    schedule.accepted and schedule.mentor_id == profile.id and schedule.request.scheduled and not schedule.request.closed):
                now = utc.localize(datetime.datetime.now())
                time_delta = (now - schedule.slot)
                total_seconds = time_delta.total_seconds()
                minutes = total_seconds / seconds
                if (minutes >= number and minutes <= number2):
                    accepted_call = AcceptedCallSchedule.objects.filter(schedule_id=schedule.id).get(completed=False)
                    token = accepted_call.token
                    if not token:
                        appCert = config('AGORA_CERT_PRIMARY')
                        appID = config('AGORA_APP_ID')
                        uid = 0
                        channel = accepted_call.channel
                        token = generateToken(uid, appID, appCert, channel, expiryTimeSec)
                        AcceptedCallSchedule.objects.filter(schedule_id=schedule.id).filter(completed=False).update(
                            token=token)
                    context = {'minutes': minutes, 'scheduled': True, 'schedule': schedule.id}
                    return render(request, 'accounts/pre_call_mentor.html', context)
                else:
                    if (minutes < number):
                        context = {'minutes': minutes, 'scheduled': False}
                        return render(request, 'accounts/pre_call_mentor.html', context)
                    else:
                        context = {'minutes': minutes, 'scheduled': False}
                        return render(request, 'accounts/pre_call_mentor.html', context)
            return redirect('mentorboard')


@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.warning(request, 'Email or password incorrect or email not verified')

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
            user = form.save()
            user_name = form.cleaned_data.get('full_name')

            email = request.POST.get('email')
            password = request.POST.get('password1')

            current_site = get_current_site(request)
            email_subject = 'Activate Your Account'
            message = render_to_string('accounts/email_verification.html', {
                'user': user_name,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.id)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(email_subject, message, to=[to_email])
            email.send()
            messages.success(request,
                             'We have sent you an email, please confirm your email address to complete registration')
            context = {'form': form, 'type': 'User'}
            return render(request, 'accounts/register.html', context)
        else:
            errors = []
            for error in form.errors.values():
                errors.append(error)
            messages.error(request, error)
    context = {'form': form, 'type': 'User'}
    return render(request, 'accounts/register.html', context)


# email verification.
def activate_account(request, uidb64, token):
    try:
        uid = str(force_bytes(urlsafe_base64_decode(uidb64)), 'utf-8')
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Your account has been activate successfully!')
        return redirect('profile')
    else:
        return HttpResponse('Activation link is invalid or expired!')


@unauthenticated_user
def mentorRegisterPage(request):
    form = RegisterMentorForm()
    if request.method == 'POST':
        form = RegisterMentorForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('full_name')
            return redirect('login')

    context = {'form': form, 'type': 'Mentor'}
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

    context = {'form': form, 'type': 'Jyolsyan'}
    return render(request, 'accounts/register.html', context)

    ## Request system


@login_required(login_url='login')
def requestCall(request):
    if request.method == "POST":

        product_id = request.POST.get('product')
        user = request.user
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        suggested_date = request.POST.get('suggested_slot')
        suggested_time = request.POST.get('period')
        institute = request.POST.get('institute')
        siblings = request.POST.get('siblings')
        language = request.POST.get('language')
        contact = request.POST.get('contact')
        hobbies = request.POST.get('hobbies')
        address = request.POST.get('address')
        guardian_name = request.POST.get('guardian')
        career_concerns = request.POST.getlist('career')
        personal_concerns = request.POST.getlist('personal')
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

        try:
            purchased_product = UserPurchases.objects.filter(user_id=user.id).filter(status=1).get(
                product_id=product_id).product
        except Exception as e:
            print(e)
            messages.error(request, 'Invalid product!')
            return redirect('dashboard')
        if (
                product_id == None or user == None or dob == None or institute == None or gender == None or siblings == None or language == None or contact == None or hobbies == None or guardian_name == None or career_concerns == None or personal_concerns == None):
            messages.warning(request, 'Please fill all the required fields!')
            return redirect('dashboard')
        career_conc = []
        personal_conc = []
        for personal_ in personal_concerns:
            if personal_ == "1":
                personal_conc.append("Interpersonal Issues")
            elif personal_ == "2":
                personal_conc.append("Family Problems")
            elif personal_ == "3":
                personal_conc.append("Medical & Health Related")
            else:
                personal_conc.append("Other")

        for career in career_concerns:
            if career == "1":
                career_conc.append("Course / Higher Education")
            elif career == "2":
                career_conc.append("Career / Job Related")
            elif career == "3":
                career_conc.append("Formulation of Study/ Academic Plans")
            else:
                career_conc.append("Other")

        try:
            pending = MentorCallRequest.objects.filter(user_id=user.id).filter(product_id=product_id).get(closed=False)
            messages.warning(request, 'Call already Requested')
            return redirect('dashboard')

        except MentorCallRequest.DoesNotExist:
            if str(purchased_product.id) == str(product_id) and purchased_product.call_required:
                MentorCallRequest.objects.create(
                    user=user,
                    product=purchased_product,
                    language=request.POST.get('language'),
                    request_date=request.POST.get('suggested_slot'),
                    requested_slot=suggested_time
                )
                try:
                    profile = UserProfile.objects.get(user_id=user.id)
                    UserProfile.objects.filter(user_id=user.id).update(
                        gender=gender,
                        siblings=request.POST.get('siblings'),
                        mobile=contact,
                        hobbies=request.POST.get('hobbies'),
                        guardian_name=request.POST.get('guardian'),
                        career_concern=career_conc,
                        personal_concern=personal_conc,
                        dob=request.POST.get('dob'),
                        institute=request.POST.get('institute'),
                        address=address
                    )
                except Exception as e:
                    UserProfile.objects.create(
                        user_id=user.id,
                        gender=gender,
                        siblings=request.POST.get('siblings'),
                        mobile=contact,
                        hobbies=request.POST.get('hobbies'),
                        guardian_name=request.POST.get('guardian'),
                        career_concern=career_conc,
                        personal_concern=personal_conc,
                        dob=request.POST.get('dob'),
                        address=address,
                        institute=institute
                    )
                messages.success(request, 'Schedule requested succesfully. Please wait for an admin to respond!')

            else:
                messages.error(request, 'An error occured!')

    return redirect('dashboard')


@login_required(login_url='login')
def requestCallAstro(request):
    if request.method == "POST":

        product_id = request.POST.get('product')
        user = request.user
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        suggested_date = request.POST.get('suggested_slot')
        suggested_time = request.POST.get('period')

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

        try:
            purchased_product = UserPurchases.objects.filter(user_id=user.id).filter(status=1).get(
                product_id=product_id).product
        except Exception as e:
            print(e)
            messages.error(request, 'Invalid product!')
            return redirect('dashboard')

        if purchased_product.prod_type == "J":
            btime = request.POST.get('time')
            bplace = request.POST.get('place')
            latlong = request.POST.get('latlong')
            q1 = request.POST.get('query1')
            q2 = request.POST.get('query2')
            dst = request.POST.get('dst')
            if dst == "1":
                dst = "Yes"
            else:
                dst = "False"
            if (
                    product_id == None or user == None or dob == None or btime == None or gender == None or bplace == None or q1 == None or q2 == None):
                messages.warning(request, 'Please fill all the required fields!')
                return redirect('dashboard')
            try:
                pending = MentorCallRequest.objects.filter(user_id=user.id).filter(product_id=product_id).get(
                    closed=False)
                messages.warning(request, 'Call already Requested')
                return redirect('dashboard')
            except MentorCallRequest.DoesNotExist:
                if str(purchased_product.id) == str(product_id) and purchased_product.call_required:
                    MentorCallRequest.objects.create(
                        user=user,
                        product=purchased_product,
                        request_date=request.POST.get('suggested_slot'),
                        requested_slot=suggested_time,
                        query1=q1,
                        query2=q2,
                    )
                    try:
                        profile = UserProfile.objects.get(user_id=user.id)
                        UserProfile.objects.filter(user_id=user.id).update(
                            gender=gender,
                            birthtime=btime,
                            dst=dst,
                            birthplace=bplace,
                            latlong=latlong,
                            dob=dob,

                        )
                    except Exception as e:
                        UserProfile.objects.create(
                            user_id=user.id,
                            gender=gender,
                            birthtime=btime,
                            dst=dst,
                            birthplace=bplace,
                            latlong=latlong,
                            dob=dob,
                        )
                    messages.success(request,
                                     'Schedule requested succesfully. Please wait for an admin to respond!')
                else:
                    messages.error(request, 'An error occured!')
                return redirect('dashboard')


@login_required(login_url='login')
def submitCareerAstro(request):
    if request.method == "POST":

        product_id = request.POST.get('product')
        user = request.user
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')

        if gender == "1":
            gender = "Male"
        elif gender == "2":
            gender = "Female"
        else:
            gender = "N/A"

        try:
            purchased_product = UserPurchases.objects.filter(user_id=user.id).filter(status=1).get(
                product_id=product_id).product
        except Exception as e:
            print(e)
            messages.error(request, 'Invalid product!')
            return redirect('dashboard')

        if purchased_product.prod_type == "A":
            btime = request.POST.get('time')
            bplace = request.POST.get('place')
            latlong = request.POST.get('latlong')
            dst = request.POST.get('dst')
            if dst == "1":
                dst = "Yes"
            else:
                dst = "False"
            if (
                    product_id == None or user == None or dob == None or btime == None or gender == None or bplace == None):
                messages.warning(request, 'Please fill all the required fields!')
                return redirect('dashboard')
            try:
                pending = MentorCallRequest.objects.filter(user_id=user.id).filter(product_id=product_id).get(
                    closed=False)
                messages.warning(request, 'Call already Requested')
                return redirect('dashboard')
            except MentorCallRequest.DoesNotExist:
                if str(purchased_product.id) == str(product_id) and purchased_product.call_required:
                    MentorCallRequest.objects.create(
                        user=user,
                        product=purchased_product,
                    )
                    try:
                        profile = UserProfile.objects.get(user_id=user.id)
                        UserProfile.objects.filter(user_id=user.id).update(
                            gender=gender,
                            birthtime=btime,
                            dst=dst,
                            birthplace=bplace,
                            latlong=latlong,
                            dob=dob,

                        )
                    except Exception as e:
                        UserProfile.objects.create(
                            user_id=user.id,
                            gender=gender,
                            birthtime=btime,
                            dst=dst,
                            birthplace=bplace,
                            latlong=latlong,
                            dob=dob,
                        )
                    messages.success(request,
                                     'Details submitted succesfully. Please wait for an admin to respond!')
                else:
                    messages.error(request, 'An error occured!')
                return redirect('dashboard')


@login_required(login_url='login')
def acceptCall(request):
    if request.method == "POST":
        schedule_id = request.POST.get('schedule')
        schedule = RequestedSchedules.objects.get(pk=schedule_id)
        call_request_id = schedule.request.id
        call_request = MentorCallRequest.objects.get(pk=call_request_id)
        form = AcceptedSchedulesForm(request.POST)
        if form.is_valid():
            if ((schedule.user_id == request.user.id or request.user.is_superuser) and not call_request.scheduled):
                AcceptedCallSchedule.objects.create(
                    schedule=schedule
                )
                RequestedSchedules.objects.filter(pk=schedule_id).update(accepted=True)
                MentorCallRequest.objects.filter(pk=call_request_id).update(scheduled=True)
                messages.success(request, 'Call Scheduled!')
            else:
                messages.error(request, 'Schedule invalid!')

    return redirect('dashboard')


@login_required(login_url='login')
@admin_user
def assignAstrologer(request):
    if request.method == "POST":
        mentor_id = request.POST.get('mentor')
        # user_id = request.POST.get('user')
        request_id = request.POST.get('request')
        mentor = MentorProfile.objects.get(id=mentor_id)
        mentor_request = MentorCallRequest.objects.get(id=request_id)
        assign = AssignSubmitReport.objects.create(mentor_request=mentor_request, astrologer=mentor)
        mentor_request.responded = True
        mentor_request.save()
        messages.success(request, 'Assigned succesfully!')
        return redirect('admin_panel')


@login_required(login_url='login')
@admin_user
def requestSchedule(request):
    if request.method == "POST":
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
        check_schedules = RequestedSchedules.objects.filter(request_id=request_id)
        clash_requests_user = MentorCallRequest.objects.filter(user_id=user_id).filter(closed=0).filter(
            responded=1).exclude(product_id=product_id)
        mentor_schedules = RequestedSchedules.objects.filter(mentor_id=mentor.id)
        if form.is_valid():
            for mentor_schedule in mentor_schedules:
                clash_request_mentor = MentorCallRequest.objects.get(pk=mentor_schedule.request_id)
                if not clash_request_mentor.closed:
                    time_delta = (mentor_schedule.slot - slot)
                    total_seconds = time_delta.total_seconds()
                    minutes = total_seconds / seconds
                    if (minutes <= 89 and minutes >= -89):
                        messages.warning(request,
                                         'Mentor Schedule clash found, please add a different time for the new schedule.')
                        return redirect('admin_panel')

            if clash_requests_user:
                for clash in clash_requests_user:
                    check_clashes = RequestedSchedules.objects.filter(request_id=clash.id)
                    for clash_req in check_clashes:
                        time_delta = (clash_req.slot - slot)
                        total_seconds = time_delta.total_seconds()
                        minutes = total_seconds / seconds
                        if (minutes <= 89 and minutes >= -89):
                            messages.warning(request,
                                             'User Schedule clash found, please add a different time for the new schedule.')
                            return redirect('admin_panel')
                        else:
                            if not check_schedules:
                                RequestedSchedules.objects.create(
                                    user=user,
                                    mentor=mentor,
                                    request=call_request,
                                    slot=slot
                                )
                                MentorCallRequest.objects.filter(pk=request_id).update(responded=True)
                                messages.success(request, 'Schedule added succesfully!')
                                return redirect('admin_panel')
                            else:
                                for schedules in check_schedules:
                                    time_delta = (schedules.slot - slot)
                                    total_seconds = time_delta.total_seconds()
                                    minutes = total_seconds / seconds
                                    if (minutes <= (number3) and minutes >= number):
                                        messages.warning(request, 'Schedule within 5 min already exist!')
                                        return redirect('admin_panel')
                                    else:
                                        RequestedSchedules.objects.create(
                                            user=user,
                                            mentor=mentor,
                                            request=call_request,
                                            slot=slot
                                        )
                                        MentorCallRequest.objects.filter(pk=request_id).update(responded=True)
                                        messages.success(request, 'Schedule added succesfully!')
                                        return redirect('admin_panel')
            else:
                if not check_schedules:
                    RequestedSchedules.objects.create(
                        user=user,
                        mentor=mentor,
                        request=call_request,
                        slot=slot
                    )
                    MentorCallRequest.objects.filter(pk=request_id).update(responded=True)
                    messages.success(request, 'Schedule added succesfully!')
                    return redirect('admin_panel')
                else:
                    for schedules in check_schedules:
                        time_delta = (schedules.slot - slot)
                        total_seconds = time_delta.total_seconds()
                        minutes = total_seconds / seconds
                        if (minutes <= number3 and minutes >= number):
                            messages.warning(request, 'Schedule within 5 min already exist!')
                            return redirect('admin_panel')
                        else:
                            RequestedSchedules.objects.create(
                                user=user,
                                mentor=mentor,
                                request=call_request,
                                slot=slot
                            )
                            MentorCallRequest.objects.filter(pk=request_id).update(responded=True)
                            messages.success(request, 'Schedule added succesfully!')
                            return redirect('admin_panel')

    return redirect('admin_panel')


@login_required(login_url='login')
def userDashboard(request):
    if not request.user.customer:
        if request.user.is_jyolsyan:
            return redirect('astroboard')
        if request.user.is_mentor:
            return redirect('mentorboard')
        if request.user.is_superuser:
            return redirect('admin_panel')

    products = Product.objects.filter(is_package=0).filter(active=1)
    purchases = request.user.user_products.filter(status=1)
    schedules = request.user.schedule_times.none()
    user_requests = request.user.mentor_request.none()
    accepted_calls = AcceptedCallSchedule.objects.none()
    results = Result.objects.filter(user_id=request.user.id).order_by('id')
    finished_calls = MentorCallRequest.objects.filter(user_id=request.user.id).filter(report_submitted=True)
    reports = FinalMentorReport.objects.none()
    career_reports = AstrologerCareerReport.objects.none()

    for report in finished_calls:
        career_reports |= AstrologerCareerReport.objects.filter(call=report.id).filter(submitted=True)

    for final in finished_calls:
        reports |= FinalMentorReport.objects.filter(call_id=final.id).filter(accepted=True)

    for purchase in purchases:
        if purchase.product.call_required:
            user_requests |= request.user.mentor_request.filter(product_id=purchase.product_id)
    for user_request in user_requests:
        if user_request.responded and not user_request.scheduled:
            schedules |= request.user.schedule_times.filter(request_id=user_request.id).filter(accepted=0)
        elif user_request.responded and user_request.scheduled and not user_request.closed:
            schedule = RequestedSchedules.objects.filter(request_id=user_request.id).get(accepted=True)
            accepted_calls |= AcceptedCallSchedule.objects.filter(schedule_id=schedule.id)
        else:
            pass
    context = {'products': products, 'purchases': purchases, 'requests': user_requests, 'schedules': schedules,
               'accepted_calls': accepted_calls, 'results': results, 'reports': reports,
               'career_reports': career_reports}
    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='login')
@jyolsyan
def astroDetailsView(request):
    if request.method == "POST":
        schedule_id = request.POST.get('schedule')
        report_id = request.POST.get('report')
        mentor_request_id = request.POST.get('mentor_request')
        if schedule_id:
            mentor_profile = MentorProfile.objects.get(user_id=request.user.id)
            schedule = RequestedSchedules.objects.filter(pk=schedule_id).filter(mentor_id=mentor_profile.id).get(
                accepted=True)
            user = schedule.user
            user_profile = UserProfile.objects.get(user_id=user.id)
            context = {'schedule': schedule, 'user': user, 'profile': user_profile}
            return render(request, 'jyothishan/details.html', context)
        if report_id:
            report = AssignSubmitReport.objects.get(id=report_id)
            mentorRequest = MentorCallRequest.objects.get(id=mentor_request_id)
            user = mentorRequest.user
            user_profile = UserProfile.objects.get(user_id=user.id)
            context = {'user': user, 'profile': user_profile}
            return render(request, 'jyothishan/details.html', context)
        else:
            return redirect('dashboard')


@login_required(login_url='login')
@admin_user
def adminDashboard(request):
    call_requests = MentorCallRequest.objects.all().order_by('-responded')
    context = {'requests': call_requests}
    return render(request, 'admin/adminpanel.html', context)


@login_required(login_url='login')
@admin_user
def adminProductView(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'admin/product.html', context)


@login_required(login_url='login')
@admin_user
def adminCustomersView(request):
    users = User.objects.all()
    context = {'Users': users}
    return render(request, 'admin/customers.html', context)


@login_required(login_url='login')
@admin_user
def adminOrdersView(request):
    orders = UserPurchases.objects.all()
    context = {'Orders': orders}
    return render(request, 'admin/orders.html', context)


@login_required(login_url='login')
@admin_user
def adminReportView(request):
    call_requests = MentorCallRequest.objects.filter(closed=True).filter(report_submitted=False).order_by('-responded')
    context = {'requests': call_requests}
    return render(request, 'admin/pending_reports.html', context)


@login_required(login_url='login')
@admin_user
def adminMentorReportView(request):
    reports = FinalMentorReport.objects.all()
    context = {'reports': reports}
    return render(request, 'admin/mentor_report.html', context)


@login_required(login_url='login')
@admin_user
def adminAstrologerReportView(request):
    reports = AstrologerCareerReport.objects.all()
    context = {'reports': reports}
    return render(request, 'admin/astrologer_report.html', context)


@login_required(login_url='login')
@admin_user
def adminMentorReportConfirmView(request, id):
    report = FinalMentorReport.objects.get(id=id)
    report.accepted = True
    report.save()
    return redirect('mentor_report')


@login_required(login_url='login')
@admin_user
def adminShowReport(request, id):
    schedule = RequestedSchedules.objects.filter(accepted=True).get(request_id=id)
    context = {'schedule': schedule, 'call_req': id}
    return render(request, 'admin/view_report_data.html', context)


@login_required(login_url='login')
@admin_user
def showSchedules(request, id):
    schedules = RequestedSchedules.objects.filter(request_id=id)
    user = User.objects.get(pk=schedules[0].user_id)
    context = {'schedules': schedules, 'requested_user': user}
    return render(request, 'admin/view_schedule.html', context)


@login_required(login_url='login')
@admin_user
def closeReport(request):
    if request.method == "POST":
        call_id = request.POST.get('call')
        MentorCallRequest.objects.filter(pk=call_id).update(report_submitted=True)
        return redirect('admin_panel')


@login_required(login_url='login')
@admin_user
def dropSchedule(request, id):
    if request.method == "POST":
        schedule = RequestedSchedules.objects.get(pk=id)
        request_id = schedule.request.id
        all_requests = RequestedSchedules.objects.filter(request_id=request_id)
        if (all_requests.count() > 1):
            schedule.delete()
        else:
            MentorCallRequest.objects.filter(pk=schedule.request.id).update(responded=False)
            schedule.delete()
            messages.success(request, 'Schedule deleted succesfully!')
    return redirect('admin_panel')


@login_required(login_url='login')
@admin_user
def respondCallRequest(request, id):
    try:
        call_request = MentorCallRequest.objects.get(pk=id)
        user = call_request.user
        mentor_products = MentorProducts.objects.filter(product_id=call_request.product.id)
        mentors = MentorProfile.objects.none()

        for mentor in mentor_products:
            mentors |= MentorProfile.objects.filter(pk=mentor.mentor_id)
        context = {'request': call_request, 'request_user': user, 'mentors': mentors}
    except MentorCallRequest.DoesNotExist:
        raise Http404("Request does not exist")
    return render(request, 'admin/call_view.html', context)


@login_required(login_url='login')
@jyolsyan
def astroDashboard(request):
    profile = MentorProfile.objects.get(user_id=request.user.id)
    schedules = RequestedSchedules.objects.filter(mentor_id=profile.id).filter(accepted=True)
    career_report = AssignSubmitReport.objects.filter(astrologer=profile, pending=True)
    context = {'schedules': schedules, 'profile': profile, 'reports': career_report}
    return render(request, 'jyothishan/dashboard.html', context)


@login_required(login_url='login')
@jyolsyan
def astroHistory(request):
    profile = MentorProfile.objects.get(user_id=request.user.id)
    schedules = RequestedSchedules.objects.filter(mentor_id=profile.id).filter(accepted=True)
    context = {'schedules': schedules, 'profile': profile}
    return render(request, 'jyothishan/past_schedules.html', context)


@login_required(login_url='login')
@jyolsyan
def astroFinishCall(request, reqid):
    schedule_id = reqid
    schedule = RequestedSchedules.objects.get(pk=schedule_id)
    if not schedule.mentor.user_id == request.user.id:
        messages.error(request, 'Invalid request')
        return redirect('dashboard')
    try:
        MentorCallRequest.objects.filter(pk=schedule.request.id).update(closed=True)
    except Exception as e:
        messages.error(request, 'Invalid request')
        return redirect('dashboard')
    return render(request, 'jyothishan/finish_call.html')


@login_required(login_url='login')
def finishCallUser(request):
    return render(request, 'accounts/finishcall.html')


def saveProfile(request):
    try:
        mob = int(request.POST.get('mobile'))
        address = request.POST.get('address')
        state = request.POST.get('state')
        pincode = int(request.POST.get('pincode'))

        if ((len(str(mob)) < 10 or len(str(mob)) > 10) or len(address) == 0 or len(state) == 0 or not (
                len(str(pincode)) == 6)):
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
        user_profile = UserProfile.objects.get(user_id=request.user.id)
        UserProfile.objects.filter(pk=user_profile.id).update(
            mobile=mob,
            address=address,
            state=state,
            pincode=pincode,
            qualification=qualification,
            stream=stream,
            institute=institute,
            mark=mark
        )
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(
            mobile=mob,
            address=address,
            state=state,
            pincode=pincode,
            user=request.user,
            qualification=qualification,
            stream=stream,
            institute=institute,
            mark=mark
        )
    return redirect('dashboard')


def requestPage(request):
    slots = []
    kv = {}
    time_slots = []
    daily_sessions = int(config('Daily_Call_Sessions'))
    if request.method == "POST":
        product_id = request.POST.get('product')
        user = request.user
        schedules = RequestedSchedules.objects.none()
        accepted_requests = MentorCallRequest.objects.none()
        product = Product.objects.get(pk=product_id)

        related_prods = Product.objects.filter(prod_type=product.prod_type)

        for product_related in related_prods:
            accepted_requests |= MentorCallRequest.objects.filter(product_id=product_related.id).filter(
                scheduled=True).filter(closed=False)
        for a_request in accepted_requests:
            schedules |= RequestedSchedules.objects.filter(request_id=a_request.id).filter(accepted=True)

        for schedule in schedules:
            now = schedule.slot
            kv.update({now: now.strftime("%d-%m-%Y") + ",No slots available"})

        results = Counter(kv.values())
        for result in results:
            if results[result] >= daily_sessions:
                slots.append(result)
    profile = UserProfile.objects.filter(user_id=user.id)
    # TODO Redirect to respective pages, check and redirect according to product type
    if product.prod_type == "M":
        context = {'slots': slots, 'product': product.id, 'profile': profile}
        return render(request, 'accounts/mentor_request.html', context)
    elif product.prod_type == "J":
        context = {'slots': slots, 'product': product.id, 'profile': profile}
        return render(request, 'accounts/astro_request.html', context)
    elif product.prod_type == "A":
        context = {'slots': slots, 'product': product.id, 'profile': profile}
        return render(request, 'accounts/astrology_submit_details.html', context)
    else:
        context = {'slots': slots, 'product': product.id, 'profile': profile}
        return render(request, 'accounts/astro_request.html', context)


def viewPrivacyPolicy(request):
    return render(request, 'base/privacy.html')


def viewTerms(request):
    return render(request, 'base/terms.html')


def viewRefund(request):
    return render(request, 'base/refund.html')


def viewAbout(request):
    return render(request, 'base/about.html')


def viewMentors(request):
    return render(request, 'base/mentors.html')


def viewContact(request):
    return render(request, 'base/contact.html')


# ERROR HANDLING..
def handler404(request, exception):
    context = {}
    response = render(request, "errors/404.html", context=context)
    response.status_code = 404
    return response


def handler500(request, exception=None):
    context = {}
    response = render(request, "errors/500.html", context=context)
    response.status_code = 500
    return response


def handler403(request, exception=None):
    context = {}
    response = render(request, "errors/403.html", context=context)
    response.status_code = 403
    return response


def handler400(request, exception=None):
    context = {}
    response = render(request, "errors/400.html", context=context)
    response.status_code = 400
    return response


@login_required(login_url='login')
def viewReport(request):
    if request.method == "POST":
        report_id = request.POST.get('report')
        report = FinalMentorReport.objects.none()
        career_report = AstrologerCareerReport.objects.none()
        try:
            report = FinalMentorReport.objects.get(pk=report_id)
        except:
            pass
        try:
            career_report = AstrologerCareerReport.objects.get(pk=report_id)
        except:
            pass
        if report:
            if not report.call.user_id == request.user.id:
                messages.error(request, 'Invalid request')
                return redirect('dashboard')
        if career_report:
            if not career_report.call.user_id == request.user.id:
                messages.error(request, 'Invalid request')
                return redirect('dashboard')
        context = {'report': report, 'career_report': career_report}
        return render(request, 'accounts/view_report.html', context)


# sitemap
def sitemap(request):
    return render(request, 'base/sitemap.xml', content_type='text/xml')
