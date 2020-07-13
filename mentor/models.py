from django.db import models


# Create your models here.
from accounts.models import User
from product.models import Product

class MentorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentor_profile')
    tags = models.CharField(max_length=255)
    experience = models.IntegerField(default=0)
    active = models.BooleanField(default=1)
    verified = models.BooleanField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Mentor: {}'.format(self.user.full_name)

    @property
    def mentor_type(self):
        if self.user.mentor:
            return 1
        else:
            return 2


class MentorProducts(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE)

    def __str__(self):
        return 'Associated Product name: {}'.format(self.product.name)
