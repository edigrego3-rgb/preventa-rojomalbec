import urllib.parse

def redondear_precio(precio):
    return round(precio)

def extraer_descripcion(nombre_producto):
    return ""  # Podemos agregar la lógica del markdown después si la necesitan en preventa

def generar_mensaje_whatsapp(carrito, total_costo, total_venta, telefono, datos_vendedor):
    """
    Genera el link de WhatsApp formateado específicamente para el preventista.
    """
    mensaje = "🛒 *NUEVO PEDIDO DE PREVENTA*\n"
    mensaje += "--------------------------------------\n"
    mensaje += f"👤 *Vendedor:* {datos_vendedor.get('nombre_vendedor', 'No especificado')}\n"
    mensaje += f"🏢 *Para entregar a:* {datos_vendedor.get('cliente_final', 'No especificado')}\n"
    
    if datos_vendedor.get('direccion'):
        mensaje += f"📍 *Dirección:* {datos_vendedor['direccion']}\n"
    if datos_vendedor.get('cuit'):
        mensaje += f"📄 *CUIT:* {datos_vendedor['cuit']}\n"
        
    mensaje += "--------------------------------------\n"
    mensaje += "*PRODUCTOS SOLICITADOS:*\n"
    
    for item in carrito:
        # Mostramos la cantidad y el nombre
        mensaje += f"• {item['cantidad']}x {item['nombre']}\n"
        # Opcional: mostrar a qué precio lo cerró con el cliente
        mensaje += f"  (Vendidos a ${item['precio_venta']:,} c/u)\n"
        
    mensaje += "--------------------------------------\n"
    mensaje += "💰 *RESUMEN FINANCIERO:*\n"
    mensaje += f"💸 *A transferir a Rojo Malbec (Costo):* $ {total_costo:,}\n"
    mensaje += f"🏷️ *Total Venta a Cliente:* $ {total_venta:,}\n"
    ganancia = total_venta - total_costo
    mensaje += f"📈 *(Ganancia Vendedor):* $ {ganancia:,}\n"
    
    mensaje_codificado = urllib.parse.quote(mensaje)
    return f"https://wa.me/{telefono}?text={mensaje_codificado}"
