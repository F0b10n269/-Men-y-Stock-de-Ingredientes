from rest_framework.routers import DefaultRouter
from .views import PlatoViewSet, IngredienteViewSet, StockViewSet

router = DefaultRouter()
router.register(r'platos', PlatoViewSet, basename='plato')
router.register(r'ingredientes', IngredienteViewSet, basename='ingrediente')
router.register(r'stock', StockViewSet, basename='stock')

urlpatterns = router.urls
