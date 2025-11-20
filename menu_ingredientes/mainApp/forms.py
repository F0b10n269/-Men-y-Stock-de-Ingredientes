from django import forms
from .models import Plato, Receta, Ingrediente, Stock, CategoriaMenu


class PlatoForm(forms.ModelForm):
    class Meta:
        model = Plato
        fields = ['nombre', 'descripcion', 'precio', 'categoria', 'activo']


class RecetaInlineForm(forms.ModelForm):
    class Meta:
        model = Receta
        fields = ['ingrediente', 'cantidad']


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['ingrediente', 'cantidad_disponible']


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = CategoriaMenu
        fields = ['nombre', 'descripcion']
