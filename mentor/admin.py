from django.contrib import admin
from .models import MentorProducts, MentorProfile

# Register your models here.
admin.site.register(MentorProfile)
admin.site.register(MentorProducts)
