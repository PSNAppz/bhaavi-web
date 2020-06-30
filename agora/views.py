from django.shortcuts import render,redirect
from django.views import View
from django.http import HttpResponse,Http404
# import model -
from accounts.models import * 
import hashlib
from decouple import config


class AgoraVideoCall(View):
    app_id=''
    channel = ''
    token = ''
    permission_class = 'IsAuthenticated'   
    channel_end_url = ''

    def get_permission(self,request,permission_class):
        if permission_class == 'AllowAny':
            return True
        elif permission_class == 'IsAuthenticated':
            return bool(request.user and request.user.is_authenticated)
        elif permission_class == 'IsAdmin':
            return bool(request.user and request.user.is_staff)
        else:
            return False

    def checkAll(self,request):
        if self.get_permission(request,self.permission_class) is True:
            return True
        else:
            return False
           

    def post(self,request):

        stat = self.checkAll(request)
        if stat:
            try:
                schedule_id = request.POST['schedule']
                requested_schedule = RequestedSchedules.objects.get(pk = schedule_id)
                if not (requested_schedule.user_id == request.user.id or requested_schedule.mentor.user_id == request.user.id) :
                    return HttpResponse('Unauthenticated')
                schedule = AcceptedCallSchedule.objects.filter(schedule_id=schedule_id).get(completed=False)
                token = schedule.token
                  
                channel = schedule.channel
                profile = UserProfile.objects.get(user_id = requested_schedule.user_id)
                return render(request,'index.html',{
                        'agora_id':self.app_id,
                        'channel':channel,
                        'token':token,
                        'profile':profile,
                        'schedule':schedule_id
                        })
            except Exception as e:
                return HttpResponse('Unknown Error')
        else:
            if not self.checkAppID(self.app_id):
                return HttpResponse('Programming Error: No App ID')
            elif not self.get_permissions(request):
                return HttpResponse('User Permission Error: No Permission')
            return HttpResponse('Unknown Error')
        

# allowed_permissions = ['AllowAny','IsAuthenticated','IsAdmin']

class Agora(AgoraVideoCall):
    app_id=config('AGORA_APP_ID')
    channel=''
    appCertificate=config('AGORA_CERT_PRIMARY')
    expiredTsInSeconds=''
    token = ''
    permission_class = 'IsAuthenticated'
    channel_end_url = ''