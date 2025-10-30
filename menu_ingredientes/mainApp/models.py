from django.db import models

class CategoriaMenu(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    
    def __str__(self):
        return self.nombre

class Ingrediente(models.Model):
    UNIDADES = [
        ('gr', 'Gramos'),
        ('kg', 'Kilogramos'),
        ('un', 'Unidades'),
        ('lt', 'Litros'),
    ]
    
    nombre = models.CharField(max_length=100)
    unidad_medida = models.CharField(max_length=2, choices=UNIDADES)
    stock_minimo = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.nombre} ({self.unidad_medida})"

class Plato(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(CategoriaMenu, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre

class Receta(models.Model):
    plato = models.ForeignKey(Plato, on_delete=models.CASCADE, related_name='recetas')
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=8, decimal_places=2)
    
    class Meta:
        unique_together = ['plato', 'ingrediente']

class Stock(models.Model):
    ingrediente = models.OneToOneField(Ingrediente, on_delete=models.CASCADE, related_name='stock')
    cantidad_disponible = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Stock {self.ingrediente.nombre}: {self.cantidad_disponible}"

class ReservaStock(models.Model):
    ESTADOS = [
        ('reservado', 'Reservado'),
        ('confirmado', 'Confirmado'),
        ('liberado', 'Liberado'),
    ]
    
    plato = models.ForeignKey(Plato, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='reservado')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    pedido_id = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Reserva {self.plato.nombre} - {self.estado}"