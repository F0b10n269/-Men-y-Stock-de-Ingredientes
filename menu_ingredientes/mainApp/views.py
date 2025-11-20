# IMPORTS
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import CategoriaMenu, Ingrediente, Plato, Receta, Stock, ReservaStock
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import PlatoForm, StockForm

# SERIALIZERS (Simples, sin DRF)
class PlatoSerializer:
    def __init__(self, instance=None, data=None, partial=False):
        self.instance = instance  # ✅ Esta línea estaba sin indentación
        self.data = data
        self.partial = partial  # Para soportar PATCH
    
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'nombre': instance.nombre,
            'descripcion': instance.descripcion,
            'precio': str(instance.precio),
            'categoria': {
                'id': instance.categoria.id if instance.categoria else None,
                'nombre': instance.categoria.nombre if instance.categoria else None
            },
            'activo': instance.activo,
            'recetas': [
                {
                    'id': receta.id,
                    'ingrediente': receta.ingrediente.nombre,
                    'unidad_medida': receta.ingrediente.unidad_medida,
                    'cantidad': str(receta.cantidad)
                } for receta in instance.recetas.all()
            ]
        }

    def is_valid(self):
        if not self.data:
            return False
        
        # Para PATCH, no requerimos todos los campos
        if not self.partial:
            required_fields = ['nombre', 'precio', 'categoria']
            for field in required_fields:
                if field not in self.data or not self.data[field]:
                    return False
        
        # Validar precio si se está actualizando
        if 'precio' in self.data:
            try:
                precio = float(self.data['precio'])
                if precio <= 0:
                    return False
            except (TypeError, ValueError):
                return False
        
        # Validar categoría si se está actualizando
        if 'categoria' in self.data:
            try:
                CategoriaMenu.objects.get(id=self.data['categoria'])
            except CategoriaMenu.DoesNotExist:
                return False

        return True

    def save(self):
        if self.instance:
            # UPDATE - Solo actualizar campos que vienen en data
            if 'nombre' in self.data:
                self.instance.nombre = self.data['nombre']
            if 'descripcion' in self.data:
                self.instance.descripcion = self.data.get('descripcion', '')
            if 'precio' in self.data:
                self.instance.precio = self.data['precio']
            if 'categoria' in self.data:
                self.instance.categoria_id = self.data['categoria']
            
            self.instance.save()
            
            # Manejar recetas si vienen en los datos
            if 'recetas' in self.data:
                # Eliminar recetas existentes y crear nuevas
                self.instance.recetas.all().delete()
                recetas_data = self.data.get('recetas', [])
                for receta_data in recetas_data:
                    ingrediente_id = receta_data.get('ingrediente_id')
                    cantidad = receta_data.get('cantidad')
                    if ingrediente_id and cantidad:
                        try:
                            ingrediente = Ingrediente.objects.get(id=ingrediente_id)
                            Receta.objects.create(
                                plato=self.instance,
                                ingrediente=ingrediente,
                                cantidad=cantidad
                            )
                        except Ingrediente.DoesNotExist:
                            continue
            
            return self.instance
        else:
            # CREATE - Código existente
            plato = Plato.objects.create(
                nombre=self.data['nombre'],
                descripcion=self.data.get('descripcion', ''),
                precio=self.data['precio'],
                categoria_id=self.data['categoria']
            )
            
            recetas_data = self.data.get('recetas', [])
            for receta_data in recetas_data:
                ingrediente_id = receta_data.get('ingrediente_id')
                cantidad = receta_data.get('cantidad')
                if ingrediente_id and cantidad:
                    try:
                        ingrediente = Ingrediente.objects.get(id=ingrediente_id)
                        Receta.objects.create(
                            plato=plato,
                            ingrediente=ingrediente,
                            cantidad=cantidad
                        )
                    except Ingrediente.DoesNotExist:
                        continue
            return plato

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

# SERVICIO DE STOCK
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

# VIEWSETS
class PlatoViewSet(viewsets.ViewSet):

    # ... tus métodos existentes (list, retrieve, create, destroy) ...
    
    def update(self, request, pk=None):
        """
        PUT /api/platos/{id}/ - Actualizar plato existente
        """
        try:
            plato = Plato.objects.get(pk=pk, activo=True)
        except Plato.DoesNotExist:
            return Response(
                {'error': 'Plato no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = PlatoSerializer(instance=plato, data=request.data)
        if serializer.is_valid():
            plato_actualizado = serializer.save()
            return Response({
                'id': plato_actualizado.id,
                'message': 'Plato actualizado exitosamente',
                'nombre': plato_actualizado.nombre
            })
        
        return Response(
            {'error': 'Datos inválidos para actualización'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def partial_update(self, request, pk=None):
        """
        PATCH /api/platos/{id}/ - Actualización parcial del plato
        """
        try:
            plato = Plato.objects.get(pk=pk, activo=True)
        except Plato.DoesNotExist:
            return Response(
                {'error': 'Plato no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Para PATCH, permitimos actualización parcial
        serializer = PlatoSerializer(instance=plato, data=request.data, partial=True)
        if serializer.is_valid():
            plato_actualizado = serializer.save()
            return Response({
                'id': plato_actualizado.id,
                'message': 'Plato actualizado parcialmente',
                'nombre': plato_actualizado.nombre
            })
        
        return Response(
            {'error': 'Datos inválidos para actualización'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    def list(self, request):
        platos = Plato.objects.filter(activo=True).select_related('categoria')
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
            {'error': 'Datos inválidos o categoría inexistente o precio no válido'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def destroy(self, request, pk=None):
        try:
            plato = Plato.objects.get(pk=pk)
            plato.activo = False
            plato.save()
            return Response({'message': 'Plato desactivado exitosamente'})
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


# -------------------- VISTAS WEB (interfaz tradicional) --------------------
def plato_list(request):
    platos = Plato.objects.filter(activo=True).select_related('categoria')
    return render(request, 'mainApp/plato_list.html', {'platos': platos})


def plato_create(request):
    if request.method == 'POST':
        form = PlatoForm(request.POST)
        if form.is_valid():
            plato = form.save()
            messages.success(request, 'Plato creado exitosamente')
            return redirect('plato_list')
    else:
        form = PlatoForm()
    return render(request, 'mainApp/plato_form.html', {'form': form, 'title': 'Nuevo Plato'})


def plato_update(request, pk):
    plato = get_object_or_404(Plato, pk=pk)
    if request.method == 'POST':
        form = PlatoForm(request.POST, instance=plato)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plato actualizado')
            return redirect('plato_list')
    else:
        form = PlatoForm(instance=plato)
    return render(request, 'mainApp/plato_form.html', {'form': form, 'title': 'Editar Plato'})


def plato_delete(request, pk):
    plato = get_object_or_404(Plato, pk=pk)
    plato.activo = False
    plato.save()
    messages.success(request, 'Plato desactivado')
    return redirect('plato_list')


def stock_list(request):
    stocks = Stock.objects.select_related('ingrediente').all()
    return render(request, 'mainApp/stock_list.html', {'stocks': stocks})


def stock_update(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock actualizado')
            return redirect('stock_list')
    else:
        form = StockForm(instance=stock)
    return render(request, 'mainApp/plato_form.html', {'form': form, 'title': 'Editar Stock'})


def simular_pedido(request):
    mensaje = None
    if request.method == 'POST':
        plato_id = request.POST.get('plato_id')
        cantidad = request.POST.get('cantidad')
        pedido_id = request.POST.get('pedido_id')
        try:
            cantidad = int(cantidad)
            stock_service = StockService()
            reserva = stock_service.validar_y_reservar_stock(plato_id, cantidad, pedido_id)
            mensaje = f"Reserva creada: {reserva.id}"
        except Exception as e:
            mensaje = str(e)

    platos = Plato.objects.filter(activo=True)
    return render(request, 'mainApp/simular_pedido.html', {'platos': platos, 'mensaje': mensaje})
