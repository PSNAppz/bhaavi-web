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
    # path('chat', views.chatpage, name='chat'),  

    # Payment flow below
    path('payment/plans', views.plansPage, name='plans'),
    path('payment/checkout', views.checkoutPage, name='checkout'), 
    path('payment/pay', views.createOrder , name="payment"), 
    path('payment/status', views.paymentStatus, name = 'payment_status'),
    path('payment/done', views.paymentSuccessPage , name="success"), 
    #path('payment/failure', views.paymentSuccessPage , name="failure"), TODO: failed page



    path('request/mentor', views.requestCall, name="mentor_request"),
    path('accept/mentor', views.acceptCall, name="accept_call"),

    # Mentor Dash
    path('mentorboard/', views.mentorDashboard, name="mentorboard"),

    # Admin panel
    path('dashboard/admin',views.adminDashboard, name="admin_panel"),
    path('dashboard/admin/request/<int:id>',views.respondCallRequest, name="respond_call"),
    path('dashboard/admin/schedule', views.requestSchedule, name="send_schedule"),
    path('dashboard/admin/schedules/<int:id>',views.showSchedules, name="show_schedules"),
    path('dashboard/admin/schedule/drop/<int:id>',views.dropSchedule, name="drop_schedule"),
 
    # agora package test view
    path('agora/',Agora.as_view(), name="agora_package")

]
