from django.urls import path
from profiles import views

urlpatterns = [
    path('', views.profile_list_view, name='list_view'),
    path('<str:username>/', views.profile_view, name='user'),
]