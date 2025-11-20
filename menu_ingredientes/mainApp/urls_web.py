from django.urls import path
from . import views

urlpatterns = [
    path('', views.plato_list, name='plato_list'),
    path('plato/new/', views.plato_create, name='plato_create'),
    path('plato/<int:pk>/edit/', views.plato_update, name='plato_update'),
    path('plato/<int:pk>/delete/', views.plato_delete, name='plato_delete'),

    path('stock/', views.stock_list, name='stock_list'),
    path('stock/<int:pk>/edit/', views.stock_update, name='stock_update'),

    path('simular/', views.simular_pedido, name='simular_pedido'),
]
