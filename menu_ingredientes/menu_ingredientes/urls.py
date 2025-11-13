from git import Repo

# URL del repositorio en GitHub
repo_url = "https://github.com/F0b10n269/-Men-y-Stock-de-Ingredientes.git"

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from mainApp.views import PlatoViewSet, IngredienteViewSet, StockViewSet
from .views import PlatoViewSet

router = DefaultRouter()
router.register(r'platos', PlatoViewSet, basename='plato')
router.register(r'ingredientes', IngredienteViewSet, basename='ingrediente')
router.register(r'stock', StockViewSet, basename='stock')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]

# Carpeta donde quieres clonar el repositorio
ruta_destino = "C:/Users/lab316.antofagasta/Downloads/menu_ingredientes_clone"

# Clonar el repositorio
Repo.clone_from(repo_url, ruta_destino)

print(" Repositorio clonado correctamente en:", ruta_destino)

