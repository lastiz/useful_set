from django.urls import path
from . import views


app_name = 'users'

urlpatterns = [
    path('login/', views.UserLogin.as_view(), name='login'),
    path('logout/', views.UserLogout.as_view(), name='logout'),
    path('register/', views.UserRegister.as_view(), name='register'),
    path('register_done/', views.UserRegisterDone.as_view(), name='register_done'),
    path('update/', views.UserUpdate.as_view(), name='user_update'),
    path('update_pass/', views.UserUpdatePass.as_view(), name='user_update_pass'),
    path('pass_reset/', views.UserResetPass.as_view(), name='reset_pass'),
    path('pass_reset_confirm/<uidb64>/<token>/', views.UserResetPassConfirm.as_view(), name='reset_pass_confirm'),
    path('profile/', views.UserProfile.as_view(), name='profile'),
    path('register_activate/<str:sign>', views.register_activate, name='register_activate'),
]
