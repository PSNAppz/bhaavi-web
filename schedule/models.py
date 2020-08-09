import uuid

from django.db import models

# Create your models here.
from accounts.models import User


class MentorCallRequest(models.Model):
    from product.models import Product

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentor_request', null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    request_date = models.CharField(max_length=20, blank=True)
    requested_slot = models.CharField(max_length=20, blank=True)
    language = models.CharField(max_length=255, null=True, blank=True)
    query1 = models.CharField(max_length=255, null=True, blank=True)
    query2 = models.CharField(max_length=255, null=True, blank=True)
    # #bride details and groom details
    # bname = models.CharField(max_length=255,null=True, blank=True)
    # bdob = models.CharField(max_length=255,null=True, blank=True)
    # btime = models.CharField(max_length=255,null=True, blank=True)
    # bplace = models.CharField(max_length=255,null=True, blank=True)
    # blatlong = models.CharField(max_length=255,null=True, blank=True)
    # gname = models.CharField(max_length=255,null=True, blank=True)
    # gdob = models.CharField(max_length=255,null=True, blank=True)
    # gtime = models.CharField(max_length=255,null=True, blank=True)
    # gplace = models.CharField(max_length=255,null=True, blank=True)
    # glatlong = models.CharField(max_length=255,null=True, blank=True)
    # # muhurtam details
    # bname = models.CharField(max_length=255,null=True, blank=True)
    # bdob = models.CharField(max_length=255,null=True, blank=True)
    # btime = models.CharField(max_length=255,null=True, blank=True)
    # bplace = models.CharField(max_length=255,null=True, blank=True)
    # blatlong = models.CharField(max_length=255,null=True, blank=True)

    responded = models.BooleanField(default=0)
    scheduled = models.BooleanField(default=0)
    closed = models.BooleanField(default=0)
    report_submitted = models.BooleanField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Request id {} Mentor type: {}'.format(self.id, self.product.name)


class RequestedSchedules(models.Model):
    from accounts.models import MentorProfile

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedule_times', null=False)
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, null=False)
    request = models.ForeignKey(MentorCallRequest, on_delete=models.CASCADE, null=False,
                                related_name='mentor_request_schedule')
    slot = models.DateTimeField()
    accepted = models.BooleanField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Mentor Call Request {} by: {} for {}'.format(self.request.id, self.user.full_name,
                                                             self.mentor.user.full_name)


def channel_gen():
    uid = uuid.uuid4()
    return uid.hex


class AcceptedCallSchedule(models.Model):
    schedule = models.ForeignKey(RequestedSchedules, on_delete=models.CASCADE, null=False,
                                 related_name='accepted_schedule')
    completed = models.BooleanField(default=0)
    channel = models.CharField(max_length=255, default=channel_gen)
    token = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Schedule id: {}'.format(self.schedule.id)


class FinalMentorReport(models.Model):
    call = models.ForeignKey(MentorCallRequest, on_delete=models.CASCADE, null=False, related_name='report_schedule')
    requirement = models.TextField(null=True, blank=True)
    diagnosis = models.TextField(null=True, blank=True)
    findings = models.TextField(null=True, blank=True)
    suggestions = models.TextField(null=True, blank=True)
    recommendation = models.TextField(null=True, blank=True)
    accepted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)


class UserSubmitDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    responded = models.BooleanField(default=0)
    scheduled = models.BooleanField(default=0)
    closed = models.BooleanField(default=0)
    report_submitted = models.BooleanField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.full_name


class AssignSubmitReport(models.Model):
    from accounts.models import MentorProfile

    mentor_request = models.ForeignKey(MentorCallRequest, on_delete=models.CASCADE, null=True)
    astrologer = models.ForeignKey(MentorProfile, on_delete=models.SET_NULL, null=True)
    pending = models.BooleanField(default=True, null=True)
    accepted = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.mentor_request.user.full_name + ":Astrologer " + self.astrologer.user.full_name


class AstrologerCareerReport(models.Model):
    call = models.ForeignKey(MentorCallRequest, on_delete=models.CASCADE, null=False)
    report = models.FileField(upload_to='career_horoscope/', null=False)
    submitted = models.BooleanField(default=False, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
