

# Recetas de los platos (ingrediente: cantidad en gramos)
recetas = {
    "pizza": {"queso": 200, "tomate": 100, "harina": 300},
    "hamburguesa": {"carne": 150, "pan": 100, "lechuga": 50},
    "ensalada": {"lechuga": 100, "tomate": 80, "aceite": 20}
}

# Inventario simulado (ingrediente: stock en gramos)
inventario = {
    "queso": 10000,
    "tomate": 8000,
    "harina": 15000,
    "carne": 5000,
    "pan": 6000,
    "lechuga": 4000,
    "aceite": 2000
}

# Reservas activas (ingrediente: cantidad reservada)
reservas = {}

# Porciones minimas por plato para alertas
PORCIONES_MINIMAS = {
    "pizza": 5,
    "hamburguesa": 5,
    "ensalada": 5
}

def validar_cambios(nuevos_ingredientes):
    #Valida que las cantidades sean positivas.#
    for cantidad in nuevos_ingredientes.values():
        if cantidad <= 0:
            return False, "Las cantidades deben ser positivas."
    return True, "OK."

def verificar_stock_suficiente(nuevos_ingredientes):
    #Verifica si hay stock para los nuevos ingredientes (simulacion para 1 porcion)#
    for ingrediente, cantidad in nuevos_ingredientes.items():
        stock_restante = inventario.get(ingrediente, 0) - reservas.get(ingrediente, 0)
        if stock_restante < cantidad:
            return False, f"No hay suficiente stock de {ingrediente}. Disponible: {stock_restante}g, necesario: {cantidad}g."
    return True, "Stock suficiente."

def verificar_alertas_stock(ingrediente):
    #Verifica alerta para un ingrediente despues de editar.#
    ingredientes_restantes = inventario.get(ingrediente, 0) - reservas.get(ingrediente, 0)
    for plato, ingredientes_necesarios in recetas.items():
        if ingrediente in ingredientes_necesarios:
            cantidad_critica = ingredientes_necesarios[ingrediente] * PORCIONES_MINIMAS[plato]
            if ingredientes_restantes < cantidad_critica:
                print(f"Alerta: Stock bajo de {ingrediente} para {plato}. Quedan {ingredientes_restantes}g, necesario {cantidad_critica}g para {PORCIONES_MINIMAS[plato]} porciones.")

def editar_plato(plato, nuevos_ingredientes):
    #Edita un plato existente con nuevos ingredientes y cantidades
    #Valida cambios y stock, actualiza receta, verifica alertas#
    if plato not in recetas:
        return False, "El plato no existe en el menu."
    
    # Validar cambios#
    exito, mensaje = validar_cambios(nuevos_ingredientes)
    if not exito:
        return False, mensaje
    
    # Verificar stock#
    exito, mensaje = verificar_stock_suficiente(nuevos_ingredientes)
    if not exito:
        return False, mensaje
    
    # Actualizar receta#
    recetas[plato] = nuevos_ingredientes
    
    # Verificar alertas para cada ingrediente editado#
    for ingrediente in nuevos_ingredientes:
        verificar_alertas_stock(ingrediente)
    
    return True, f"Plato {plato} editado exitosamente: {nuevos_ingredientes}."

# Prueba interactiva#
def main():
    print("Menú actual:", recetas)
    plato = input("Ingrese el plato a editar (ejemplo, pizza): ")
    
    # Ejemplo de nuevos ingredientes 
    nuevos_ingredientes = {}  
    print("Ingrese nuevos ingredientes (por ejemplo, queso:200, tomate:150): ")
    while True:
        ing = input("Ingrediente (o 'fin' para terminar): ")
        if ing == 'fin':
            break
        cant = int(input("Cantidad (en gramos): "))
        nuevos_ingredientes[ing] = cant
    
    if nuevos_ingredientes:
        exito, mensaje = editar_plato(plato, nuevos_ingredientes)
        print(mensaje)
        print("Menu actualizado:", recetas)
    else:
        print("No se edito nada.")

if __name__ == "__main__":
    main()