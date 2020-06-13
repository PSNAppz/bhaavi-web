from django.urls import path
from . import views
from agora.views import Agora

urlpatterns = [
    path('', views.homePage,name="home"),
    path('user/profile', views.profilePage, name="profile"),
    path('dashboard', views.userDashboard,name="dashboard"),
    path('login', views.loginPage, name="login"),
    path('mentor/register', views.mentorRegisterPage, name="mentor_register"),
    path('jyolsyan/register', views.jyolsyanRegisterPage, name="jyolsyan_register"),
    path('user/register', views.userRegisterPage, name="register"),
    path('logout', views.logoutUser, name="logout"),  
    path('pricing', views.pricingDetails,name="pricing"),
    path('chat', views.chatpage, name='chat'),  
    # Payment flow below
    path('plans', views.plansPage, name='plans'),
    path('checkout', views.checkoutPage, name='checkout'), 
    path('payment_success', views.paymentSuccessPage, name="success_payment"),  
    # agora package test view
    path('agora/',Agora.as_view(app_id='60c0a4a0d014433e9870a5ba3b6c8977',channel='1'), name="agora_package"),
]
