from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from mentor.decorators import mentor

from schedule.models import RequestedSchedules, MentorCallRequest, FinalMentorReport
from mentor.models import MentorProfile
from accounts.models import UserProfile


@login_required(login_url='login')
@mentor
def mentorDashboard(request):
    profile = MentorProfile.objects.get(user_id=request.user.id)
    schedules = RequestedSchedules.objects.filter(mentor_id=profile.id).filter(accepted=True)
    # reports = MentorCallRequest.objects.filter(mentor_id=profile.id).filter(re)
    context = {'schedules': schedules, 'profile': profile}
    return render(request, 'mentor/dashboard.html', context)


@login_required(login_url='login')
@mentor
def mentorHistory(request):
    profile = MentorProfile.objects.get(user_id=request.user.id)
    schedules = RequestedSchedules.objects.filter(mentor_id=profile.id).filter(accepted=True)
    context = {'schedules': schedules, 'profile': profile}
    return render(request, 'mentor/past_schedules.html', context)


@login_required(login_url='login')
@mentor
def endCall(request, reqid):
    schedule_id = reqid
    schedule = RequestedSchedules.objects.get(pk=schedule_id)
    if not schedule.mentor.user_id == request.user.id:
        messages.error(request, 'Invalid request')
        return redirect('dashboard')
    try:
        callreq = MentorCallRequest.objects.get(pk=schedule.request.id)
    except Exception as e:
        messages.error(request, 'Invalid request')
        return redirect('dashboard')
    user = callreq.user
    context = {'user': user, 'call': callreq, 'schedule': schedule.id}
    return render(request, 'mentor/report.html', context)


@login_required(login_url='login')
@mentor
def mentorDetailsView(request):
    if request.method == "POST":
        schedule_id = request.POST.get('schedule')
        mentor_profile = MentorProfile.objects.get(user_id=request.user.id)
        schedule = RequestedSchedules.objects.filter(pk=schedule_id).filter(mentor_id=mentor_profile.id).get(
            accepted=True)
        user = schedule.user
        user_profile = UserProfile.objects.get(user_id=user.id)
        context = {'schedule': schedule, 'user': user, 'profile': user_profile}
        return render(request, 'mentor/details.html', context)
    else:
        return redirect('dashboard')


@login_required(login_url='login')
@mentor
def submitReport(request):
    if request.method == "POST":
        schedule_id = request.POST.get('schedule')
        requirement = request.POST.get('requirement')
        diagnosis = request.POST.get('diagnosis')
        findings = request.POST.get('findings')
        suggestions = request.POST.get('suggestions')
        recommendation = request.POST.get('recommendation')

        if requirement == None or diagnosis == None or findings == None or suggestions == None or recommendation == None:
            messages.warning(request, 'Please fill all the details!')
            return redirect('dashboard')

        schedule = RequestedSchedules.objects.get(pk=schedule_id)
        if not schedule.mentor.user_id == request.user.id:
            messages.error(request, 'Invalid request')
            return redirect('dashboard')
        try:
            callreq = MentorCallRequest.objects.get(pk=schedule.request.id)
        except Exception as e:
            messages.error(request, 'Invalid request')
            return redirect('dashboard')
        user = callreq.user
        try:
            call = FinalMentorReport.objects.get(call_id=callreq.id)
            messages.error(request, 'Report already submitted for this!')
            return redirect('dashboard')
        except Exception as e:
            FinalMentorReport.objects.create(
                call=callreq,
                requirement=requirement,
                diagnosis=diagnosis,
                findings=findings,
                suggestions=suggestions,
                recommendation=recommendation
            )
            MentorCallRequest.objects.filter(pk=schedule.request.id).update(report_submitted=True, closed=True)
            messages.success(request, 'Thank you! Report sumbitted succesfully!')
            return redirect('mentorboard')
