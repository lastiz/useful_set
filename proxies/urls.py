from django.urls import path
from . import views


app_name = 'proxies'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('proxies_list/', views.proxies_list, name='proxies_list'),
]
