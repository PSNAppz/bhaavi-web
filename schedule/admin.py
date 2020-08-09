from django.contrib import admin

# Register your models here.
from schedule.models import AcceptedCallSchedule, RequestedSchedules, MentorCallRequest, FinalMentorReport, \
    UserSubmitDetails, AssignSubmitReport, AstrologerCareerReport

admin.site.register(AcceptedCallSchedule)
admin.site.register(RequestedSchedules)
admin.site.register(MentorCallRequest)
admin.site.register(FinalMentorReport)
admin.site.register(UserSubmitDetails)
admin.site.register(AssignSubmitReport)
admin.site.register(AstrologerCareerReport)
