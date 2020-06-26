from django.db import models
from accounts.models import *


class Question(models.Model):
    question = models.CharField(max_length=255, blank=True)
    strongly_agree = models.IntegerField(default=4)
    agree = models.IntegerField(default=3)
    disagree = models.IntegerField(default=2)
    strongly_disagree = models.IntegerField(default=1)
    category = models.CharField(max_length=2, blank=True)

    def __str__(self):
        return 'Question category: {}'.format(self.category)      

class QuestionAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answer_user')
    purchase = models.ForeignKey(UserPurchases, on_delete=models.CASCADE, related_name='picset_purchase')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.IntegerField(default=2, null=False)
    timestamp = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return 'User: {}'.format(self.user.full_name)              

class Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='result_user')
    attendee_name = models.CharField(max_length=255,blank=True)
    pragmatic_score = models.CharField(max_length=5, blank=True)
    industrious_score = models.CharField(max_length=5, blank=True)
    creative_score = models.CharField(max_length=5, blank=True)
    socialite_score = models.CharField(max_length=5, blank=True)
    explorer_score = models.CharField(max_length=5, blank=True)
    traditional_score = models.CharField(max_length=5, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return 'User name: {}'.format(self.user.name)        