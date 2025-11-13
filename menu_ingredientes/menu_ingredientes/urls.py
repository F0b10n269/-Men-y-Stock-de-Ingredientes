from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from mainApp.views import PlatoViewSet, IngredienteViewSet, StockViewSet

#  Configuración correcta del router
router = DefaultRouter()
router.register(r'platos', PlatoViewSet, basename='plato')
router.register(r'ingredientes', IngredienteViewSet, basename='ingrediente')
router.register(r'stock', StockViewSet, basename='stock')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
