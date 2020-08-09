from django.urls import path

from . import views


app_name = 'en_dict'

urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path('add_word/', views.WordAddView.as_view(), name='add_word'),
    path('training/', views.training, name='training'),
]
