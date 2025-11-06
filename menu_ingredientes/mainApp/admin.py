from django.contrib import admin
from .models import CategoriaMenu, Ingrediente, Plato, Receta, Stock, ReservaStock

@admin.register(CategoriaMenu)
class CategoriaMenuAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre']

@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'unidad_medida', 'stock_minimo']
    list_filter = ['unidad_medida']
    search_fields = ['nombre']

class RecetaInline(admin.TabularInline):
    model = Receta
    extra = 1

@admin.register(Plato)
class PlatoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'categoria', 'activo']
    list_filter = ['categoria', 'activo']
    search_fields = ['nombre']
    inlines = [RecetaInline]

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['ingrediente', 'cantidad_disponible']
    search_fields = ['ingrediente__nombre']

@admin.register(ReservaStock)
class ReservaStockAdmin(admin.ModelAdmin):
    list_display = ['plato', 'cantidad', 'estado', 'fecha_creacion', 'pedido_id']
    list_filter = ['estado', 'fecha_creacion']
    search_fields = ['plato__nombre', 'pedido_id']
