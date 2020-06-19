from django.shortcuts import render,redirect
from django.views import View
from django.http import HttpResponse,Http404
# import model -
from accounts.models import User  # for testing only
import hashlib
from decouple import config



class AgoraVideoCall(View):
    app_id=''
    channel = ''
    token = ''
    permission_class = 'IsAuthenticated'   
    channel_end_url = ''

#for testing used name of the logged user as channel name. 
#change it to the random channel_name stored in the table.
    def createChannel(self,request):
        try:

            data = User.objects.get(email=self.request.user)
            channel = data.full_name
            return channel
        except:
            raise Http404("Request is not valid/ Schedule Not Found")
# Token generation
    # def generateSignalingToken(
    #     account,
    #     appID,
    #     appCertificate,
    #     expiredTsInSeconds):
    #     version = "1"
    #     expired = str(expiredTsInSeconds)
    #     account="test@test"
    #     content = account + appID + appCertificate + expired
    #     md5sum = hashlib.md5(content.encode('utf-8')).hexdigest()
    #     token = "%s:%s:%s:%s" % (version, appID, expired, md5sum)
    #     return token
    


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

        stat = self.checkAll(request)
        print(self.app_id,self.channel)
        # channel = self.createChannel(request)   #sample function.
        if stat:
            return render(request,'index.html',{
                    'agora_id':self.app_id,
                    'channel':self.createChannel(request), 
                    # 'channel':self.channel,
                    # 'token':self.generateSignalingToken(self.app_id,self.appCertificate,self.expiredTsInSeconds),
                    'channel_end_url':self.channel_end_url
                    })
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
    app_id=''
    channel=''
    # appCertificate='a378db0f912f4b169e4f0208511de1a4'
    # expiredTsInSeconds='60'
    # token = '123'
    permission_class = 'IsAuthenticated'
    channel_end_url = '/dashboard'