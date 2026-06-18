"""
CHATBOT DE GESTION DE VACACIONES - CON PERSISTENCIA EN CSV
Trabajo Practico Integrador - Organizacion Empresarial

"""

from datetime import datetime  # Para manejar y validar fechas
import csv                      # Para leer y escribir el archivo de persistencia
import os                       # Para verificar existencia de archivos y limpiar pantalla

# ==================== BASE DE DATOS ====================
# Diccionario que simula la base de datos de empleados.
# Clave: ID del empleado | Valor: nombre y saldo de dias disponibles.
# empleados = {
#     101: {"nombre": "Juan Perez", "saldo": 14},
#     102: {"nombre": "Maria Gomez", "saldo": 21},
#     103: {"nombre": "Carlos Lopez", "saldo": 7},
#     104: {"nombre": "Ana Martinez", "saldo": 28},
#     105: {"nombre": "Pedro Sanchez", "saldo": 10},
# }

# Contador global para asignar IDs unicos a cada nueva solicitud
ultimo_id_solicitud = 0

# Lista en memoria con todas las solicitudes cargadas desde el CSV
solicitudes = []

# ==================== FUNCIONES DE CSV ====================

def inicializar_csv():
    """Crea el archivo CSV con los encabezados si no existe.
    Retorna True si lo creo, False si ya existia."""
    global ultimo_id_solicitud
    if not os.path.exists('solicitudes.csv'):
        # El archivo no existe: crearlo con la fila de encabezados
        with open('solicitudes.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['id_solicitud', 'empleado_id', 'empleado_nombre',
                           'fecha_inicio', 'fecha_fin', 'dias_solicitados',
                           'estado', 'fecha_solicitud'])
        return True  # Se creo el archivo
    return False     # El archivo ya existia

def cargar_solicitudes():
    """Lee el CSV y carga todas las solicitudes previas en la lista global.
    Tambien actualiza el contador de IDs para no repetir numeros."""
    global ultimo_id_solicitud, solicitudes

    solicitudes = []  # Limpiar la lista antes de cargar

    # Si el archivo no existe aun, inicializarlo vacio y retornar
    if not os.path.exists('solicitudes.csv'):
        inicializar_csv()
        return []

    try:
        with open('solicitudes.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)  # Leer como diccionario usando la primera fila como clave
            for row in reader:
                try:
                    # Convertir cada fila del CSV a un diccionario con tipos correctos
                    solicitud = {
                        'id_solicitud':    int(row.get('id_solicitud', 0)),
                        'empleado_id':     int(row.get('empleado_id', 0)),
                        'empleado_nombre': row.get('empleado_nombre', ''),
                        'fecha_inicio':    row.get('fecha_inicio', ''),
                        'fecha_fin':       row.get('fecha_fin', ''),
                        'dias_solicitados':int(row.get('dias_solicitados', 0)),
                        'estado':          row.get('estado', ''),
                        'fecha_solicitud': row.get('fecha_solicitud', '')
                    }
                    solicitudes.append(solicitud)

                    # Actualizar el contador al maximo ID encontrado para evitar duplicados
                    if solicitud['id_solicitud'] > ultimo_id_solicitud:
                        ultimo_id_solicitud = solicitud['id_solicitud']

                except (ValueError, KeyError):
                    # Si una fila del CSV esta corrupta o incompleta, la ignoramos
                    continue
    except Exception as e:
        print(f"⚠️ Error al leer CSV: {e}")

    return solicitudes

def guardar_solicitud(empleado_id, empleado_nombre, fecha_inicio_str,
                      fecha_fin_str, dias, estado):
    """Persiste una nueva solicitud tanto en el CSV como en la lista en memoria.
    Retorna el ID unico asignado a la nueva solicitud."""
    global ultimo_id_solicitud, solicitudes

    # Generar un nuevo ID unico incrementando el contador global
    ultimo_id_solicitud += 1
    nuevo_id = ultimo_id_solicitud

    # Registrar el momento exacto en que se hace la solicitud
    fecha_solicitud = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # --- Persistencia en disco: agregar una nueva fila al CSV ---
    try:
        with open('solicitudes.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                nuevo_id, empleado_id, empleado_nombre,
                fecha_inicio_str, fecha_fin_str, dias, estado, fecha_solicitud
            ])
    except Exception as e:
        print(f"⚠️ Error al guardar: {e}")

    # --- Persistencia en memoria: agregar a la lista global ---
    # Esto permite consultar el historial sin releer el archivo
    solicitudes.append({
        'id_solicitud':    nuevo_id,
        'empleado_id':     empleado_id,
        'empleado_nombre': empleado_nombre,
        'fecha_inicio':    fecha_inicio_str,
        'fecha_fin':       fecha_fin_str,
        'dias_solicitados':dias,
        'estado':          estado,
        'fecha_solicitud': fecha_solicitud
    })

    return nuevo_id

# Al iniciar el programa, leer el CSV para recuperar el historial previo
cargar_solicitudes()
print(f"📋 {len(solicitudes)} solicitudes cargadas desde CSV")

# ==================== MÁQUINA DE ESTADOS ====================
# Diccionario que guarda el estado actual de cada empleado en la conversacion.
# Clave: emp_id | Valor: dict con 'paso' (estado actual) y 'datos' (datos temporales).
# Ejemplo: { 102: { "paso": "esperando_fecha_fin", "datos": { "fecha_inicio": ... } } }
estados = {}

# ==================== FUNCIONES DEL BOT ====================

def limpiar_pantalla():
    """Limpia la consola. Compatible con Windows (cls) y Linux/Mac (clear)."""
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_menu(emp_id):
    """Construye y retorna el string del menu principal personalizado para el empleado."""
    nombre = empleados[emp_id]["nombre"]
    saldo  = empleados[emp_id]["saldo"]

    # Filtrar solo las solicitudes del empleado actual para mostrar su total
    mis_solicitudes  = [s for s in solicitudes if s["empleado_id"] == emp_id]
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
    """Valida que la cadena tenga formato DD/MM/AAAA y no sea una fecha pasada.
    Retorna (objeto_datetime, None) si es valida, o (None, mensaje_error) si no."""
    try:
        fecha = datetime.strptime(fecha_str, "%d/%m/%Y")  # Intentar parsear la fecha
        # Rechazar fechas anteriores a hoy (no se pueden pedir vacaciones en el pasado)
        if fecha.date() < datetime.now().date():
            return None, "⚠️ La fecha no puede ser anterior a hoy"
        return fecha, None  # Fecha valida
    except ValueError:
        # El formato no coincide con DD/MM/AAAA
        return None, "❌ Formato invalido. Usa DD/MM/AAAA (ej: 25/12/2026)"

def consultar_saldo(emp_id):
    """Devuelve el saldo actual"""
    saldo = empleados[emp_id]["saldo"]
    nombre = empleados[emp_id]["nombre"]
    return f"\n💰 {nombre}, tu saldo actual es: {saldo} dias disponibles.\n"

def mostrar_historial(emp_id):
    """Retorna un string con el historial de solicitudes del empleado.
    Muestra las ultimas 10 solicitudes ordenadas de mas reciente a mas antigua."""
    # Filtrar solo las solicitudes del empleado actual
    mis_solicitudes = [s for s in solicitudes if s["empleado_id"] == emp_id]

    if not mis_solicitudes:
        return "\n📭 No tenes solicitudes previas.\n"

    texto  = "\n" + "═" * 60 + "\n"
    texto += "                 📋 TUS SOLICITUDES 📋\n"
    texto += "═" * 60 + "\n\n"

    # Tomar las ultimas 10 y revertirlas para mostrar la mas reciente primero
    for s in reversed(mis_solicitudes[-10:]):
        # Elegir icono segun si fue aprobada o rechazada
        estado_texto = "✅ APROBADA" if s["estado"] == "aprobado" else "❌ RECHAZADA"

        texto += f"   {estado_texto}\n"
        texto += f"   📅 {s['fecha_inicio']}  →  {s['fecha_fin']}\n"
        texto += f"   📊 {s['dias_solicitados']} dias solicitados\n"
        texto += f"   🕐 {s['fecha_solicitud']}\n"
        texto += "   " + "─" * 56 + "\n\n"

    return texto

def procesar_solicitud_vacaciones(emp_id, fecha_inicio, fecha_fin,
                                    fecha_inicio_str, fecha_fin_str):
    """Aplica las reglas de negocio para aprobar o rechazar una solicitud.
    Retorna una tupla (estado, dias, mensaje) con el resultado."""
    saldo_actual = empleados[emp_id]["saldo"]
    nombre       = empleados[emp_id]["nombre"]

    # Regla: la fecha de inicio debe ser anterior o igual a la de fin
    if fecha_inicio > fecha_fin:
        return "rechazado", 0, "❌ La fecha de inicio no puede ser posterior a la fecha de fin."

    # Calcular la cantidad de dias pedidos (ambos extremos son inclusivos)
    dias = (fecha_fin - fecha_inicio).days + 1

    # GATEWAY: verificar si el empleado tiene saldo suficiente
    if dias > saldo_actual:
        # No hay saldo: guardar como rechazada y notificar al empleado
        guardar_solicitud(emp_id, nombre, fecha_inicio_str,
                          fecha_fin_str, dias, "rechazado")
        return "rechazado", dias, (
            f"❌ SOLICITUD RECHAZADA\n"
            f"   Necesitas {dias} dias, pero tenes solo {saldo_actual} dias disponibles."
        )

    # APROBAR: hay saldo suficiente, descontarlo del balance del empleado
    nuevo_saldo = saldo_actual - dias
    empleados[emp_id]["saldo"] = nuevo_saldo  # Actualizar saldo en memoria

    # Guardar solicitud aprobada en CSV y en memoria
    guardar_solicitud(emp_id, nombre, fecha_inicio_str,
                      fecha_fin_str, dias, "aprobado")

    return "aprobado", dias, (
        f"✅ SOLICITUD APROBADA!\n"
        f"   Dias solicitados: {dias}\n"
        f"   Nuevo saldo: {nuevo_saldo} dias"
    )

# ==================== PROCESADOR PRINCIPAL ====================

def procesar_mensaje(emp_id, mensaje):
    """Nucleo de la maquina de estados. Recibe el ID del empleado y el texto
    ingresado, y devuelve la respuesta correspondiente segun el paso actual.

    Estados posibles:
      - 'menu'                  : el empleado esta viendo el menu principal
      - 'esperando_fecha_inicio': se le pidio la fecha de inicio de vacaciones
      - 'esperando_fecha_fin'   : se le pidio la fecha de fin de vacaciones
    """
    # Si es la primera vez que este empleado interactua, inicializar su estado
    if emp_id not in estados:
        estados[emp_id] = {"paso": "menu"}

    paso = estados[emp_id]["paso"]  # Estado actual del empleado

    # ========== ESTADO: MENU PRINCIPAL ==========
    if paso == "menu":
        if mensaje == "1":
            return consultar_saldo(emp_id)          # Mostrar saldo disponible

        elif mensaje == "2":
            # Iniciar el flujo de solicitud: pasar al siguiente estado
            estados[emp_id]["paso"]  = "esperando_fecha_inicio"
            estados[emp_id]["datos"] = {}  # Diccionario temporal para guardar las fechas
            return "\n📅 INGRESA LA FECHA DE INICIO (DD/MM/AAAA)\n   Ejemplo: 15/12/2026\n   Escribe 'cancelar' para volver\n"

        elif mensaje == "3":
            return mostrar_historial(emp_id)        # Mostrar solicitudes previas

        elif mensaje == "0":
            return "SALIR"                          # Señal especial para cerrar sesion

        else:
            return "❌ Opcion invalida. Usa 1, 2, 3 o 0."

    # ========== ESTADO: ESPERANDO FECHA DE INICIO ==========
    elif paso == "esperando_fecha_inicio":
        if mensaje.lower() == "cancelar":
            estados[emp_id]["paso"] = "menu"  # Volver al menu sin guardar nada
            return "✅ Operacion cancelada."

        # Validar que la fecha tenga el formato correcto y no sea pasada
        fecha, error = validar_fecha(mensaje)
        if error:
            return f"{error}\n📅 Ingresa fecha valida (DD/MM/AAAA) o 'cancelar':"

        # Guardar la fecha de inicio en los datos temporales del empleado
        estados[emp_id]["datos"]["fecha_inicio"]     = fecha    # Objeto datetime
        estados[emp_id]["datos"]["fecha_inicio_str"] = mensaje  # Texto original para el CSV
        estados[emp_id]["paso"] = "esperando_fecha_fin"         # Avanzar al siguiente estado
        return f"✅ Fecha inicio: {mensaje}\n\n📅 INGRESA LA FECHA DE FIN (DD/MM/AAAA)\n   Escribe 'cancelar' para volver\n"

    # ========== ESTADO: ESPERANDO FECHA DE FIN ==========
    elif paso == "esperando_fecha_fin":
        if mensaje.lower() == "cancelar":
            estados[emp_id]["paso"] = "menu"  # Cancelar y volver al menu
            return "✅ Operacion cancelada."

        # Validar formato y que no sea fecha pasada
        fecha, error = validar_fecha(mensaje)
        if error:
            return f"{error}\n📅 Ingresa fecha valida (DD/MM/AAAA) o 'cancelar':"

        # Recuperar la fecha de inicio que se guardo en el estado anterior
        fecha_inicio     = estados[emp_id]["datos"]["fecha_inicio"]
        fecha_fin        = fecha
        fecha_inicio_str = estados[emp_id]["datos"]["fecha_inicio_str"]
        fecha_fin_str    = mensaje

        # Verificar que la fecha fin no sea anterior a la de inicio
        if fecha_fin < fecha_inicio:
            return "❌ La fecha fin no puede ser anterior a la fecha inicio.\n📅 Ingresa una fecha posterior o 'cancelar':"

        # Ambas fechas son validas: procesar la solicitud con las reglas de negocio
        estado, dias, respuesta = procesar_solicitud_vacaciones(
            emp_id, fecha_inicio, fecha_fin, fecha_inicio_str, fecha_fin_str
        )

        # Flujo completado: volver al menu principal
        estados[emp_id]["paso"] = "menu"
        return f"\n{respuesta}\n"

    # Este punto no deberia alcanzarse nunca en condiciones normales
    return "⚠️ Error interno. Reinicia el programa."

# ==================== PROGRAMA PRINCIPAL ====================

def main():
    """Funcion principal del programa. Contiene tres niveles de bucles:
      1. Bucle externo  : permite cambiar de empleado sin cerrar el programa.
      2. Bucle de sesion: mantiene al empleado en el menu hasta que elija salir.
      3. Bucle de accion: valida la opcion post-sesion (consultar otro o salir).
    """
    print("=" * 60)
    print("      🏢 CHATBOT DE GESTION DE VACACIONES 🏢")
    print("      Con persistencia en CSV")
    print("=" * 60)

    # ── BUCLE EXTERNO: se repite cada vez que un empleado termina su sesion ──
    while True:

        # Mostrar la lista de empleados disponibles antes de pedir el ID
        print("\n📋 EMPLEADOS REGISTRADOS:")
        print("─" * 40)
        for id_emp, datos in empleados.items():
            print(f"   ID {id_emp}  →  {datos['nombre']}  (saldo: {datos['saldo']} dias)")
        print("─" * 40)

        # Pedir ID hasta recibir uno valido (numero entero que exista en el diccionario)
        while True:
            try:
                emp_id = int(input("\n👉 Ingresa tu ID de empleado: "))
                if emp_id in empleados:
                    break  # ID valido: salir del bucle de validacion
                print("❌ ID no encontrado. Usa: 101, 102, 103, 104 o 105")
            except ValueError:
                print("❌ Ingresa un numero valido")  # Entrada no numerica

        # Mostrar el menu inicial para el empleado identificado
        print(mostrar_menu(emp_id))

        # ── BUCLE DE SESION: el empleado opera hasta que elige la opcion 0 ──
        while True:
            opcion = input("> ").strip()

            # Opcion 0 ingresada directamente (sin pasar por procesar_mensaje)
            if opcion == "0":
                print("\n" + "=" * 60)
                print(f"   📊 Solicitudes realizadas en esta sesion: {len([s for s in solicitudes if s['empleado_id'] == emp_id])}")
                print("=" * 60)
                break  # Terminar la sesion del empleado actual

            # Procesar la opcion a traves de la maquina de estados
            respuesta = procesar_mensaje(emp_id, opcion)

            # La maquina de estados tambien puede devolver la señal de salida
            if respuesta == "SALIR":
                print("\n" + "=" * 60)
                print(f"   📊 Solicitudes realizadas en esta sesion: {len([s for s in solicitudes if s['empleado_id'] == emp_id])}")
                print("=" * 60)
                break  # Terminar la sesion del empleado actual

            # Imprimir la respuesta generada por el bot
            print(respuesta)

            # Si el flujo regreso al menu (no hay pasos pendientes), mostrarlo de nuevo
            if emp_id in estados and estados[emp_id]["paso"] == "menu":
                print(mostrar_menu(emp_id))

        # ── BUCLE DE ACCION POST-SESION: continuar con otro empleado o cerrar ──
        print("\n╔══════════════════════════════════════════════════════════╗")
        print("║              ¿QUE DESEAS HACER AHORA?                   ║")
        print("╠══════════════════════════════════════════════════════════╣")
        print("║                                                          ║")
        print("║     [1]  Consultar otro empleado                         ║")
        print("║     [0]  Salir del programa                              ║")
        print("║                                                          ║")
        print("╚══════════════════════════════════════════════════════════╝")

        while True:
            siguiente = input("👉 Elige una opcion (1 o 0): ").strip()
            if siguiente == "1":
                break          # Volver al inicio del bucle externo (nuevo empleado)
            elif siguiente == "0":
                # Cerrar el programa completamente
                print("\n" + "=" * 60)
                print("   👋 ¡Hasta luego! Gracias por usar el sistema.")
                print("=" * 60)
                return         # Salir de main() y terminar el proceso
            else:
                print("❌ Opcion invalida. Ingresa 1 o 0.")

# ==================== EJECUTAR ====================
# Punto de entrada: solo se ejecuta si se corre el archivo directamente,
# no cuando se importa como modulo desde otro script.
if __name__ == "__main__":
    main()