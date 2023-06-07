from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('user/', views.UserList.as_view()),
    path('snowconn/', views.snowflakeconn , name = 'snowflakeconn'),
    path('get/', views.getreq , name = 'getreq'),
    path('establish/', views.establishConn , name = 'establish'),
    path('col/', views.column_names , name = 'col'),
    path('patch/', views.updatereq , name = 'patch'),
    path('del/', views.deletereq , name = 'delete'),
    path('post/', views.insertreq , name = 'post'),
    path('raw/', views.raw , name = 'raw'),
    # path('cdk/', views.cdk, name = 'cdk'),

]