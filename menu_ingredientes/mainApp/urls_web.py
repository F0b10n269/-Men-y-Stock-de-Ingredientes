from django.urls import path
from . import views

urlpatterns = [
    path('', views.plato_list, name='plato_list'),
    path('plato/new/', views.plato_create, name='plato_create'),
    path('plato/<int:pk>/edit/', views.plato_update, name='plato_update'),
    path('plato/<int:pk>/delete/', views.plato_delete, name='plato_delete'),

    # Categorías
    path('categorias/', views.categoria_list, name='categoria_list'),
    path('categoria/new/', views.categoria_create, name='categoria_create'),
    path('categoria/<int:pk>/edit/', views.categoria_update, name='categoria_update'),
    path('categoria/<int:pk>/delete/', views.categoria_delete, name='categoria_delete'),

    path('stock/', views.stock_list, name='stock_list'),
    path('stock/new/', views.stock_create, name='stock_create'),
    # Ingredientes
    path('ingredientes/', views.ingrediente_list, name='ingrediente_list'),
    path('ingrediente/new/', views.ingrediente_create, name='ingrediente_create'),
    path('ingrediente/<int:pk>/edit/', views.ingrediente_update, name='ingrediente_update'),
    path('ingrediente/<int:pk>/delete/', views.ingrediente_delete, name='ingrediente_delete'),
    path('stock/<int:pk>/edit/', views.stock_update, name='stock_update'),

    path('simular/', views.simular_pedido, name='simular_pedido'),
]
