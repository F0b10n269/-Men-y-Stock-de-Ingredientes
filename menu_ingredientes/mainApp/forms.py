from django import forms
from .models import Plato, Receta, Ingrediente, Stock


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
