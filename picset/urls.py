from django.urls import path,re_path
from . import views

urlpatterns = [
    path('dashboard/PICSET', views.takeTest,name="picset_test"),
    path('dashboard/PICSET/result', views.getResult,kwargs={'id': None},name="picset_result"),

    path('dashboard/PICSET/api/v1/getQuestion', views.getQuestion, name="getQuestion"),
    path('dashboard/PICSET/pdf/<int:id>', views.getPDF,kwargs={'id': None},name="picset_view"),
    # path('dashboard/PICSET/pdf/<int:id>/download', views.downloadPDF,kwargs={'id': None},name="picset_pdf"),


]