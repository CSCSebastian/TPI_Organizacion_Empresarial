# Chatbot de Gestión de Vacaciones

**Trabajo Práctico Integrador — Organización Empresarial | UTN**

---

## Descripción

Sistema de gestión de solicitudes de vacaciones basado en un chatbot de consola. Permite a los empleados consultar su saldo de días disponibles, solicitar períodos de vacaciones y revisar su historial, todo con persistencia automática en archivos CSV.

El bot implementa una **máquina de estados** por empleado que guía la conversación paso a paso, validando fechas y aplicando las reglas de negocio (control de saldo, rechazo automático por saldo insuficiente, etc.).

---

## Estructura del proyecto

```
TPI_Organizacion_Empresarial/
├── bot_vacaciones.py   # Código principal del chatbot
├── empleados.csv       # Base de datos de empleados (lectura)
├── solicitudes.csv     # Historial de solicitudes (generado automáticamente)
└── README.md
```

---

## Requisitos

- Python 3.7 o superior
- No requiere librerías externas (solo módulos de la biblioteca estándar: `csv`, `os`, `datetime`)

---

## Instalación y ejecución

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd TPI_Organizacion_Empresarial

# 2. Ejecutar el bot
python bot_vacaciones.py
```

---

## Uso

Al iniciar, el programa muestra la lista de empleados registrados y solicita un ID para identificarse.

| Opción | Acción |
|--------|--------|
| `1` | Consultar saldo de días disponibles |
| `2` | Solicitar un período de vacaciones |
| `3` | Ver historial de solicitudes |
| `0` | Cerrar sesión |

Durante el flujo de solicitud, ingresar las fechas en formato `DD/MM/AAAA`. En cualquier momento se puede escribir `cancelar` para volver al menú sin guardar cambios.

---

## Empleados de ejemplo

| ID | Nombre | Saldo (días) | Antigüedad |
|----|--------|:------------:|:----------:|
| 101 | Juan Pérez | 14 | 3 años |
| 102 | María Gómez | 21 | 8 años |
| 103 | Carlos López | 7 | 1 año |
| 104 | Ana Martínez | 28 | 12 años |
| 105 | Pedro Sánchez | 10 | 2 años |

---

## Persistencia

- **`empleados.csv`** — Se lee al iniciar el programa. Contiene el saldo inicial de cada empleado.
- **`solicitudes.csv`** — Se crea automáticamente si no existe. Cada solicitud (aprobada o rechazada) queda registrada con fecha y hora.

> El saldo descontado por vacaciones aprobadas se actualiza en memoria durante la sesión. Para persistir los saldos entre sesiones, editar `empleados.csv` manualmente.

---

## Tecnologías

- **Python 3.7+**
- **CSV** — persistencia de datos sin base de datos externa
- **Máquina de estados** — control del flujo de conversación por empleado

---

## Autores

- Crespi Claudio Sebastián
- Doglioli Nicolás Daniel