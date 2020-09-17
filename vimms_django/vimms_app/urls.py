from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    path('simple_ms1', views.simple_ms1, name='simple_ms1'),
    path('dia', views.dia, name='dia'),
    path('multiple_sample', views.multiple_sample, name='multiple_sample'),
    path('top_n', views.top_n, name='top_n'),
]