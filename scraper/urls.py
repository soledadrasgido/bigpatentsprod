from django.urls import path
from .views import EcuacionDelete
#from .views import EcuacionUpdate
from . import views

scraper_patterns = ([
    path('detail/<int:pk>/', views.Patente, name='ecuacion'),
    path('analisis/<int:pk>/<str:fecha1>/<str:fecha2>/<str:paisel>/', views.AnalisisEcuacion, name='analisis'),
    path('analisisproyecto/<int:pk>/', views.AnalisisProyecto, name='analisisproyecto'),
    path('create/<int:pk>/', views.EcuacionCreate, name='create' ),
    #path('update/<int:pk>/', views.EcuacionUpdate, name='update'),
    path('delete/<int:pk>/', EcuacionDelete.as_view(), name='delete'),
], 'scraper')