from django.urls import path
from . import views
from agora.views import Agora
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Basic page URLs
    path('', views.homePage, name="home"),
    path('dashboard/profile', views.profilePage, name="profile"),
    path('dashboard/profile/save', views.saveProfile, name="profile_save"),
    path('dashboard', views.userDashboard, name="dashboard"),
    path('dashboard/view', views.viewReport, name="report_view"),
    path('dashboard/conference/finish', views.finishCallUser, name="call_end"),
    path('sitemap', views.sitemap, name="sitemap"),

    path('login', views.loginPage, name="login"),
    path('mentor/register', views.mentorRegisterPage, name="mentor_register"),
    path('jyolsyan/register', views.jyolsyanRegisterPage, name="jyolsyan_register"),
    path('user/register', views.userRegisterPage, name="register"),
    path('logout', views.logoutUser, name="logout"),

    # Mentor Dash
    path('mentorboard/', views.mentorDashboard, name="mentorboard"),
    path('mentorboard/viewDetails', views.mentorDetailsView, name="view_details_mentor"),
    path('mentorboard/prevDetails', views.mentorHistory, name="view_history_mentor"),
    path('mentorboard/submitReport', views.submitReport, name="submit_report"),
    path('dashboard/conference/end/<reqid>', views.endCall, name="end_call"),

    path('dashboard/careerReport/<id>', views.submitCareerReport, name="career-report"),
    path('dashboard/submitCareerReport/<id>', views.submitCareerReportHoroscope, name="submit_career_report"),

    # Payment flow below

    path('request/mentor', views.requestCall, name="mentor_request"),
    path('request/astro', views.requestCallAstro, name="astro_request"),
    path('request/astroCareer', views.submitCareerAstro, name="astro_career"),

    path('request/details', views.requestPage, name="request_details"),
    path('accept/mentor', views.acceptCall, name="accept_call"),

    # Jyolsyan Dash
    path('astroboard', views.astroDashboard, name="astroboard"),
    path('astroboard/viewDetails', views.astroDetailsView, name="view_details_astro"),
    path('astroboard/prevDetails', views.astroHistory, name="view_history_astro"),
    path('astroboard/endCall/<reqid>', views.astroFinishCall, name="astro_call_finish"),

    # Admin panel
    path('dashboard/admin', views.adminDashboard, name="admin_panel"),
    path('dashboard/astrologerCallRequest', views.astrologerCallRequest, name="astrologer_call_request"),
    path('dashboard/reports', views.adminReportView, name="admin_panel_reports"),
    path('dashboard/astrologerReports', views.adminAstrologerReportView, name="astrologer_report"),
    path('dashboard/admin/request/<int:id>', views.respondCallRequest, name="respond_call"),
    path('dashboard/admin/report/<int:id>', views.adminShowReport, name="admin_show_report"),
    path('dashboard/admin/report/close', views.closeReport, name="close_report"),


    path('dashboard/admin/couponView', views.couponAdminView, name="coupon_view"),
    path('dashboard/admin/createCouponView', views.couponCreateView, name="coupon_create_view"),
    path('dashboard/admin/createCoupon', views.couponCreate, name="create_coupon"),

    path('dashboard/admin/product', views.adminProductView, name="product"),
    path('dashboard/admin/customers', views.adminCustomersView, name="customers"),
    path('dashboard/admin/orders', views.adminOrdersView, name="orders"),
    path('dashboard/admin/mentorReport', views.adminMentorReportView, name="mentor_report"),
    path('dashboard/admin/adminMentorReportConfirmView/<int:id>', views.adminMentorReportConfirmView,
         name="mentor_report_confirm"),
    # path('dashboard/admin/mentorReport', views.adminMentorReportView, name="mentor_report"),

    path('dashboard/admin/schedule', views.requestSchedule, name="send_schedule"),
    path('dashboard/admin/assignAstrologer', views.assignAstrologer, name="assign_astrologer"),
    path('dashboard/admin/schedules/<int:id>', views.showSchedules, name="show_schedules"),
    path('dashboard/admin/schedule/drop/<int:id>', views.dropSchedule, name="drop_schedule"),

    # Conference call URLs
    path('dashboard/ready', views.callDetails, name="call_details"),
    path('dashboard/conference/', Agora.as_view(), name="conference"),

    # Static pages
    path('privacy_policy', views.viewPrivacyPolicy, name="privacy"),
    path('terms_and_conditions', views.viewTerms, name="terms"),
    path('refund_policy', views.viewRefund, name="refund"),
    path('about', views.viewAbout, name="about"),
    path('mentors', views.viewMentors, name="mentors"),
    path('contact', views.viewContact, name="contact"),

    # email_verification
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),

    # Password reset pages

    # path('reset_password', views.ResetPasswordRequestView.as_view(), name="reset_password"),

    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),

]
