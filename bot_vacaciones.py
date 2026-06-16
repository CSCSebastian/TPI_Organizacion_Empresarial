"""
CHATBOT DE GESTION DE VACACIONES - CON PERSISTENCIA EN CSV
Trabajo Practico Integrador - Organizacion Empresarial
"""

from datetime import datetime
import csv
import os

# ==================== BASE DE DATOS ====================
empleados = {
    101: {"nombre": "Juan Perez", "saldo": 14},
    102: {"nombre": "Maria Gomez", "saldo": 21},
    103: {"nombre": "Carlos Lopez", "saldo": 7},
    104: {"nombre": "Ana Martinez", "saldo": 28},
    105: {"nombre": "Pedro Sanchez", "saldo": 10},
}

# Contador para ID de solicitud
ultimo_id_solicitud = 0
solicitudes = []

# ==================== FUNCIONES DE CSV ====================

def inicializar_csv():
    """Crea el archivo CSV con los encabezados si no existe"""
    global ultimo_id_solicitud
    if not os.path.exists('solicitudes.csv'):
        with open('solicitudes.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['id_solicitud', 'empleado_id', 'empleado_nombre', 
                           'fecha_inicio', 'fecha_fin', 'dias_solicitados', 
                           'estado', 'fecha_solicitud'])
        return True
    return False

def cargar_solicitudes():
    """Carga las solicitudes existentes desde el CSV"""
    global ultimo_id_solicitud, solicitudes
    
    solicitudes = []
    
    # Si el archivo no existe, crearlo
    if not os.path.exists('solicitudes.csv'):
        inicializar_csv()
        return []
    
    try:
        with open('solicitudes.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    solicitud = {
                        'id_solicitud': int(row.get('id_solicitud', 0)),
                        'empleado_id': int(row.get('empleado_id', 0)),
                        'empleado_nombre': row.get('empleado_nombre', ''),
                        'fecha_inicio': row.get('fecha_inicio', ''),
                        'fecha_fin': row.get('fecha_fin', ''),
                        'dias_solicitados': int(row.get('dias_solicitados', 0)),
                        'estado': row.get('estado', ''),
                        'fecha_solicitud': row.get('fecha_solicitud', '')
                    }
                    solicitudes.append(solicitud)
                    if solicitud['id_solicitud'] > ultimo_id_solicitud:
                        ultimo_id_solicitud = solicitud['id_solicitud']
                except (ValueError, KeyError):
                    # Si alguna fila tiene error, la saltamos
                    continue
    except Exception as e:
        print(f"⚠️ Error al leer CSV: {e}")
    
    return solicitudes

def guardar_solicitud(empleado_id, empleado_nombre, fecha_inicio_str, 
                      fecha_fin_str, dias, estado):
    """Guarda una nueva solicitud en el CSV"""
    global ultimo_id_solicitud, solicitudes
    
    ultimo_id_solicitud += 1
    nuevo_id = ultimo_id_solicitud
    fecha_solicitud = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # Guardar en CSV
    try:
        with open('solicitudes.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                nuevo_id, empleado_id, empleado_nombre,
                fecha_inicio_str, fecha_fin_str, dias, estado, fecha_solicitud
            ])
    except Exception as e:
        print(f"⚠️ Error al guardar: {e}")
    
    # Guardar en memoria
    solicitudes.append({
        'id_solicitud': nuevo_id,
        'empleado_id': empleado_id,
        'empleado_nombre': empleado_nombre,
        'fecha_inicio': fecha_inicio_str,
        'fecha_fin': fecha_fin_str,
        'dias_solicitados': dias,
        'estado': estado,
        'fecha_solicitud': fecha_solicitud
    })
    
    return nuevo_id

# Cargar solicitudes al iniciar
cargar_solicitudes()
print(f"📋 {len(solicitudes)} solicitudes cargadas desde CSV")

# ==================== MÁQUINA DE ESTADOS ====================
estados = {}

# ==================== FUNCIONES DEL BOT ====================

def limpiar_pantalla():
    """Limpia la pantalla (opcional, para mejor visualizacion)"""
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_menu(emp_id):
    """Muestra el menu principal"""
    nombre = empleados[emp_id]["nombre"]
    saldo = empleados[emp_id]["saldo"]
    
    # Calcular cuántas solicitudes tiene
    mis_solicitudes = [s for s in solicitudes if s["empleado_id"] == emp_id]
    total_solicitudes = len(mis_solicitudes)
    
    return f"""
╔══════════════════════════════════════════════════════════╗
║                 SISTEMA DE GESTION DE VACACIONES         ║
╠══════════════════════════════════════════════════════════╣
║  👤 Hola {nombre}                                          
║  📊 Tu saldo actual: {saldo} dias                             
║  📋 Solicitudes realizadas: {total_solicitudes}                   
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║     [1]  Consultar mi saldo                              ║
║     [2]  Solicitar vacaciones                            ║
║     [3]  Ver mi historial                                ║
║     [0]  Salir                                           ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
👉 Elige una opcion (1, 2, 3 o 0): """

def validar_fecha(fecha_str):
    """Valida formato DD/MM/AAAA y que no sea anterior a hoy"""
    try:
        fecha = datetime.strptime(fecha_str, "%d/%m/%Y")
        if fecha.date() < datetime.now().date():
            return None, "⚠️ La fecha no puede ser anterior a hoy"
        return fecha, None
    except ValueError:
        return None, "❌ Formato invalido. Usa DD/MM/AAAA (ej: 25/12/2026)"

def consultar_saldo(emp_id):
    """Devuelve el saldo actual"""
    saldo = empleados[emp_id]["saldo"]
    nombre = empleados[emp_id]["nombre"]
    return f"\n💰 {nombre}, tu saldo actual es: {saldo} dias disponibles.\n"

def mostrar_historial(emp_id):
    """Muestra el historial de solicitudes"""
    mis_solicitudes = [s for s in solicitudes if s["empleado_id"] == emp_id]
    
    if not mis_solicitudes:
        return "\n📭 No tenes solicitudes previas.\n"
    
    texto = "\n" + "═" * 60 + "\n"
    texto += "                 📋 TUS SOLICITUDES 📋\n"
    texto += "═" * 60 + "\n\n"
    
    for s in reversed(mis_solicitudes[-10:]):  # Mostrar mas recientes primero
        if s["estado"] == "aprobado":
            estado_texto = "✅ APROBADA"
        else:
            estado_texto = "❌ RECHAZADA"
        
        texto += f"   {estado_texto}\n"
        texto += f"   📅 {s['fecha_inicio']}  →  {s['fecha_fin']}\n"
        texto += f"   📊 {s['dias_solicitados']} dias solicitados\n"
        texto += f"   🕐 {s['fecha_solicitud']}\n"
        texto += "   " + "─" * 56 + "\n\n"
    
    return texto

def procesar_solicitud_vacaciones(emp_id, fecha_inicio, fecha_fin, 
                                    fecha_inicio_str, fecha_fin_str):
    """Procesa la solicitud con las reglas de negocio"""
    saldo_actual = empleados[emp_id]["saldo"]
    nombre = empleados[emp_id]["nombre"]
    
    # Validar orden de fechas
    if fecha_inicio > fecha_fin:
        return "rechazado", 0, "❌ La fecha de inicio no puede ser posterior a la fecha de fin."
    
    # Calcular dias
    dias = (fecha_fin - fecha_inicio).days + 1
    
    # GATEWAY: validar saldo disponible
    if dias > saldo_actual:
        # Guardar solicitud rechazada
        guardar_solicitud(emp_id, nombre, fecha_inicio_str, 
                          fecha_fin_str, dias, "rechazado")
        return "rechazado", dias, f"❌ SOLICITUD RECHAZADA\n   Necesitas {dias} dias, pero tenes solo {saldo_actual} dias disponibles."
    
    # APROBAR: descontar saldo
    nuevo_saldo = saldo_actual - dias
    empleados[emp_id]["saldo"] = nuevo_saldo
    
    # Guardar solicitud aprobada
    guardar_solicitud(emp_id, nombre, fecha_inicio_str, 
                      fecha_fin_str, dias, "aprobado")
    
    return "aprobado", dias, f"✅ SOLICITUD APROBADA!\n   Dias solicitados: {dias}\n   Nuevo saldo: {nuevo_saldo} dias"

# ==================== PROCESADOR PRINCIPAL ====================

def procesar_mensaje(emp_id, mensaje):
    """Maquina de estados - procesa cada mensaje"""
    
    # Inicializar estado
    if emp_id not in estados:
        estados[emp_id] = {"paso": "menu"}
    
    paso = estados[emp_id]["paso"]
    
    # ========== MENU PRINCIPAL ==========
    if paso == "menu":
        if mensaje == "1":
            return consultar_saldo(emp_id)
        
        elif mensaje == "2":
            estados[emp_id]["paso"] = "esperando_fecha_inicio"
            estados[emp_id]["datos"] = {}
            return "\n📅 INGRESA LA FECHA DE INICIO (DD/MM/AAAA)\n   Ejemplo: 15/12/2026\n   Escribe 'cancelar' para volver\n"
        
        elif mensaje == "3":
            return mostrar_historial(emp_id)
        
        elif mensaje == "0":
            return "SALIR"
        
        else:
            return "❌ Opcion invalida. Usa 1, 2, 3 o 0."
    
    # ========== ESPERANDO FECHA INICIO ==========
    elif paso == "esperando_fecha_inicio":
        if mensaje.lower() == "cancelar":
            estados[emp_id]["paso"] = "menu"
            return "✅ Operacion cancelada."
        
        fecha, error = validar_fecha(mensaje)
        if error:
            return f"{error}\n📅 Ingresa fecha valida (DD/MM/AAAA) o 'cancelar':"
        
        estados[emp_id]["datos"]["fecha_inicio"] = fecha
        estados[emp_id]["datos"]["fecha_inicio_str"] = mensaje
        estados[emp_id]["paso"] = "esperando_fecha_fin"
        return f"✅ Fecha inicio: {mensaje}\n\n📅 INGRESA LA FECHA DE FIN (DD/MM/AAAA)\n   Escribe 'cancelar' para volver\n"
    
    # ========== ESPERANDO FECHA FIN ==========
    elif paso == "esperando_fecha_fin":
        if mensaje.lower() == "cancelar":
            estados[emp_id]["paso"] = "menu"
            return "✅ Operacion cancelada."
        
        fecha, error = validar_fecha(mensaje)
        if error:
            return f"{error}\n📅 Ingresa fecha valida (DD/MM/AAAA) o 'cancelar':"
        
        fecha_inicio = estados[emp_id]["datos"]["fecha_inicio"]
        fecha_fin = fecha
        fecha_inicio_str = estados[emp_id]["datos"]["fecha_inicio_str"]
        fecha_fin_str = mensaje
        
        if fecha_fin < fecha_inicio:
            return "❌ La fecha fin no puede ser anterior a la fecha inicio.\n📅 Ingresa una fecha posterior o 'cancelar':"
        
        # Procesar la solicitud
        estado, dias, respuesta = procesar_solicitud_vacaciones(
            emp_id, fecha_inicio, fecha_fin, fecha_inicio_str, fecha_fin_str
        )
        
        # Volver al menu
        estados[emp_id]["paso"] = "menu"
        return f"\n{respuesta}\n"
    
    return "⚠️ Error interno. Reinicia el programa."

# ==================== PROGRAMA PRINCIPAL ====================

def main():
    """Funcion principal con bucle while que muestra el menu constantemente"""
    
    print("=" * 60)
    print("      🏢 CHATBOT DE GESTION DE VACACIONES 🏢")
    print("      Con persistencia en CSV")
    print("=" * 60)
    
    # Mostrar empleados registrados
    print("\n📋 EMPLEADOS REGISTRADOS:")
    print("─" * 40)
    for id_emp, datos in empleados.items():
        print(f"   ID {id_emp}  →  {datos['nombre']}  (saldo: {datos['saldo']} dias)")
    print("─" * 40)
    
    # Seleccionar empleado
    while True:
        try:
            emp_id = int(input("\n👉 Ingresa tu ID de empleado: "))
            if emp_id in empleados:
                break
            print("❌ ID no encontrado. Usa: 101, 102, 103, 104 o 105")
        except ValueError:
            print("❌ Ingresa un numero valido")
    
    # Bucle principal - muestra menu hasta que el usuario salga
    print(mostrar_menu(emp_id))
    
    while True:
        opcion = input("> ").strip()
        
        if opcion == "0":
            print("\n" + "=" * 60)
            print("   👋 ¡Hasta luego! Gracias por usar el sistema.")
            print(f"   📊 Total de solicitudes realizadas: {len([s for s in solicitudes if s['empleado_id'] == emp_id])}")
            print("=" * 60)
            break
        
        respuesta = procesar_mensaje(emp_id, opcion)
        
        if respuesta == "SALIR":
            print("\n" + "=" * 60)
            print("   👋 ¡Hasta luego! Gracias por usar el sistema.")
            print(f"   📊 Total de solicitudes realizadas: {len([s for s in solicitudes if s['empleado_id'] == emp_id])}")
            print("=" * 60)
            break
        
        # Mostrar respuesta del bot
        print(respuesta)
        
        # Si no estamos en medio de una solicitud, mostrar el menu nuevamente
        if emp_id in estados and estados[emp_id]["paso"] == "menu":
            print(mostrar_menu(emp_id))

# ==================== EJECUTAR ====================
if __name__ == "__main__":
    main()