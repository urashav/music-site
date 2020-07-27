from django.urls import path
from music import views

urlpatterns = [
    path('', views.home, name='index'),
    path('legal/', views.legal, name='legal'),
    path('play/<int:track_id>/', views.play, name='play'),
    path('download/<str:slug>/', views.download, name='download'),
    path('<str:slug>/', views.detail, name='detail'),
]
