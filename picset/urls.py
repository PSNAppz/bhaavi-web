from django.urls import path,re_path
from . import views

urlpatterns = [
    path('dashboard/PICSET', views.takeTest,name="picset_test"),
    re_path(r'PICSET/result/^(?P<album_id>[0-9])/$', views.getResult,kwargs={'id': None},name="picset_result"),
    path('PICSET/result', views.getResult,kwargs={'id': None},name="picset_result"),

    path('dashboard/PICSET/api/v1/getQuestion', views.getQuestion, name="getQuestion"),
]