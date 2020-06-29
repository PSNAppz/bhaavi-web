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

    # def get_permission(self,request,permission_class):
    #     if permission_class == 'AllowAny':
    #         return True
    #     elif permission_class == 'IsAuthenticated':
    #         return bool(request.user and request.user.is_authenticated)
    #     elif permission_class == 'IsAdmin':
    #         return bool(request.user and request.user.is_staff)
    #     else:
    #         return False

    # def checkAll(self,request):
    #     if self.get_permission(request,self.permission_class) is True:
    #         return True
    #     else:
    #         return False

    def get_permission(self,request,permission_class):
            if permission_class == 'AllowAny':
                return True
            elif permission_class == 'IsAuthenticated':
                return bool(request.user and request.user.is_authenticated)
            elif permission_class == 'IsAdmin':
                return bool(request.user and request.user.is_staff)
            else:
                return False


    def checkAppID(self,appId):
        if appId == '':
            return False
        else:
            return True

    def checkChannel(self,channel):
        if channel == '':
            return False
        else:
            return True

    def checkAll(self,request):
        if self.get_permission(request,self.permission_class) == True and self.checkAppID(self.app_id) == True :# and self.checkChannel(self.channel) == True:
            return True
        else:
            return False       

    def get(self,request):

        # stat = self.checkAll(request)
        # if stat:
        #     try:
        #         # schedule_id = request.POST['schedule']
        #         # requested_schedule = RequestedSchedules.objects.get(pk = schedule_id)
        #         # if not (requested_schedule.user_id == request.user.id or requested_schedule.mentor.user_id == request.user.id) :
        #         #     return HttpResponse('Unauthenticated')
        #         # schedule = AcceptedCallSchedule.objects.filter(schedule_id=schedule_id).get(completed=False)
        #         # token = schedule.token
        #         # channel = schedule.channel
        #         return render(request,'index.html',{
        #                 'agora_id':self.app_id,
        #                 'channel':self.channel,
        #                 'token':self.token,
        #                 'channel_end_url':self.channel_end_url
        #                 })
        #     except Exception as e:
        #         return HttpResponse('Unknown Error')
        # else:
        #     if not self.checkAppID(self.app_id):
        #         return HttpResponse('Programming Error: No App ID')
        #     elif not self.get_permissions(request):
        #         return HttpResponse('User Permission Error: No Permission')
        #     return HttpResponse('Unknown Error')

        stat = self.checkAll(request)
        print(self.app_id,self.channel)
        # channel = self.createChannel(request)   #sample function.
        if stat:
            context={
                    'agora_id':self.app_id,
                    # 'channel':self.createChannel(request), 
                     'channel':self.channel,
                    # 'token':self.generateSignalingToken(self.app_id,self.appCertificate,self.expiredTsInSeconds),
                    'channel_end_url':self.channel_end_url,
                    # 'user_details':User.objects.get(id=request.user.id)
                    }
            return render(request,'index.html',context)
        else:
            if not self.checkAppID(self.app_id):
                return HttpResponse('Programming Error: No App ID')
            elif not self.get_permissions(request):
                return HttpResponse('User Permission Error: No Permission')
            elif not self.checkChannel(request,self.channel):
                return HttpResponse('Programming Error: No Channel Name')
        return HttpResponse('Unknown Error')
        

# allowed_permissions = ['AllowAny','IsAuthenticated','IsAdmin']

class Agora(AgoraVideoCall):
    app_id=config('AGORA_APP_ID')
    channel='12'
    # appCertificate=config('AGORA_CERT_PRIMARY')
    # expiredTsInSeconds=''
    # token = '15313'
    permission_class = 'AllowAny'
    channel_end_url = '/dashboard'