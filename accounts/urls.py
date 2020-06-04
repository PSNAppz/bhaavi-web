from django.urls import path
from . import views

urlpatterns = [
    path('', views.homePage,name="home"),
    path('profile', views.profilePage),
    path('dashboard', views.userDashboard,name="dashboard"),
    path('login', views.loginPage, name="login"),
    path('mentor/register', views.mentorRegisterPage, name="register"),
    path('jyolsyan/register', views.jyolsyanRegisterPage, name="register"),
    path('user/register', views.userRegisterPage, name="register"),
    path('logout', views.logoutUser, name="logout"),   
]
