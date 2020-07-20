from django.contrib import admin

# Register your models here.
from schedule.models import AcceptedCallSchedule, RequestedSchedules, MentorCallRequest

admin.site.register(AcceptedCallSchedule)
admin.site.register(RequestedSchedules)
admin.site.register(MentorCallRequest)