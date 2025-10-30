# ✅ IMPORTS CORRECTOS
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import CategoriaMenu, Ingrediente, Plato, Receta, Stock, ReservaStock

# ✅ SERIALIZERS SIMPLES (sin DRF)
class PlatoSerializer:
    def __init__(self, instance=None, data=None):
        self.instance = instance
        self.data = data
    
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'nombre': instance.nombre,
            'descripcion': instance.descripcion,
            'precio': str(instance.precio),
            'categoria': instance.categoria.nombre if instance.categoria else None,
            'activo': instance.activo,
            'recetas': [
                {
                    'ingrediente': receta.ingrediente.nombre,
                    'cantidad': str(receta.cantidad)
                } for receta in instance.recetas.all()
            ]
        }
    
    def is_valid(self):
        if not self.data:
            return False
        required_fields = ['nombre', 'precio', 'categoria']
        for field in required_fields:
            if field not in self.data or not self.data[field]:
                return False
        return True
    
    def save(self):
        if self.instance:
            # Update
            self.instance.nombre = self.data['nombre']
            self.instance.descripcion = self.data.get('descripcion', '')
            self.instance.precio = self.data['precio']
            self.instance.categoria_id = self.data['categoria']
            self.instance.save()
            return self.instance
        else:
            # Create
            return Plato.objects.create(
                nombre=self.data['nombre'],
                descripcion=self.data.get('descripcion', ''),
                precio=self.data['precio'],
                categoria_id=self.data['categoria']
            )

class IngredienteSerializer:
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'nombre': instance.nombre,
            'unidad_medida': instance.unidad_medida,
            'stock_minimo': instance.stock_minimo
        }

class StockSerializer:
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'ingrediente': instance.ingrediente.nombre,
            'cantidad_disponible': str(instance.cantidad_disponible)
        }

# ✅ SERVICIO DE STOCK
class StockService:
    
    @transaction.atomic
    def validar_y_reservar_stock(self, plato_id, cantidad, pedido_id):
        try:
            plato = Plato.objects.get(id=plato_id, activo=True)
            
            # Verificar stock para cada ingrediente
            for receta in plato.recetas.all():
                stock = Stock.objects.get(ingrediente=receta.ingrediente)
                cantidad_necesaria = receta.cantidad * cantidad
                
                if stock.cantidad_disponible < cantidad_necesaria:
                    raise ValidationError(
                        f"Stock insuficiente de {receta.ingrediente.nombre}. "
                        f"Necesario: {cantidad_necesaria}, Disponible: {stock.cantidad_disponible}"
                    )
            
            # Crear reserva
            reserva = ReservaStock.objects.create(
                plato=plato,
                cantidad=cantidad,
                pedido_id=pedido_id,
                estado='reservado'
            )
            
            # Bloquear stock reservado
            for receta in plato.recetas.all():
                stock = Stock.objects.get(ingrediente=receta.ingrediente)
                cantidad_necesaria = receta.cantidad * cantidad
                stock.cantidad_disponible -= cantidad_necesaria
                stock.save()
            
            return reserva
            
        except Plato.DoesNotExist:
            raise ValidationError("Plato no encontrado o inactivo")
        except Stock.DoesNotExist:
            raise ValidationError("Error en configuración de stock")

# ✅ VIEWSETS
class PlatoViewSet(viewsets.ViewSet):
    
    def list(self, request):
        platos = Plato.objects.filter(activo=True)
        serializer = PlatoSerializer()
        data = [serializer.to_representation(plato) for plato in platos]
        return Response(data)
    
    def retrieve(self, request, pk=None):
        try:
            plato = Plato.objects.get(pk=pk, activo=True)
            serializer = PlatoSerializer()
            return Response(serializer.to_representation(plato))
        except Plato.DoesNotExist:
            return Response(
                {'error': 'Plato no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def create(self, request):
        serializer = PlatoSerializer(data=request.data)
        if serializer.is_valid():
            plato = serializer.save()
            return Response(
                {'id': plato.id, 'message': 'Plato creado exitosamente'},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'error': 'Datos inválidos'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def destroy(self, request, pk=None):
        try:
            plato = Plato.objects.get(pk=pk)
            plato.activo = False
            plato.save()
            return Response({'message': 'Plato desactivado'})
        except Plato.DoesNotExist:
            return Response(
                {'error': 'Plato no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class IngredienteViewSet(viewsets.ViewSet):
    
    def list(self, request):
        ingredientes = Ingrediente.objects.all()
        serializer = IngredienteSerializer()
        data = [serializer.to_representation(ing) for ing in ingredientes]
        return Response(data)

class StockViewSet(viewsets.ViewSet):
    
    def list(self, request):
        stocks = Stock.objects.all()
        serializer = StockSerializer()
        data = [serializer.to_representation(stock) for stock in stocks]
        return Response(data)
    
    @action(detail=False, methods=['post'])
    def validar_reservar(self, request):
        plato_id = request.data.get('plato_id')
        cantidad = request.data.get('cantidad')
        pedido_id = request.data.get('pedido_id')
        
        # Validaciones básicas
        if not plato_id or not cantidad or not pedido_id:
            return Response(
                {'error': 'plato_id, cantidad y pedido_id son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                return Response(
                    {'error': 'cantidad debe ser mayor a 0'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (TypeError, ValueError):
            return Response(
                {'error': 'cantidad debe ser un número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            stock_service = StockService()
            reserva = stock_service.validar_y_reservar_stock(plato_id, cantidad, pedido_id)
            return Response({
                'success': True,
                'reserva_id': reserva.id,
                'message': 'Stock reservado exitosamente'
            })
        except ValidationError as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)