from django.urls import path
from .views import PatentDetailView, PatentUpdate, PatentDelete
from . import views

patentes_patterns = ([
    path('detail/<int:pk>/', PatentDetailView.as_view(), name='patentes_detail'),
    path('update/<int:pk>/', PatentUpdate.as_view(), name='update'),
    path('delete/<int:pk>/', PatentDelete.as_view(), name='delete'),
], 'patentes')