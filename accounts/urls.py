from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('profile', views.profile),
    #path('/', admin.site.urls),
]
