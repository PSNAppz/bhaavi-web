from django.urls import path
from . import views

urlpatterns = [
    path('', views.homePage,name="home"),
    path('profile', views.profilePage),
    path('login', views.loginPage, name="login"),
    path('register', views.registerPage, name="register"),
    path('logout/', views.logoutUser, name="logout"),   
]
