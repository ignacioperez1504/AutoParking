# AutoParking

**Sistema distribuido de gestión de parqueadero en tiempo real — C++ para lógica de simulación y Python (Tkinter) para visualización gráfica en red local.**

[![C++](https://img.shields.io/badge/C++-Logic%20%26%20Simulation-00599C?style=flat-square&logo=cplusplus&logoColor=white)](https://isocpp.org)
[![Python](https://img.shields.io/badge/Python-GUI%20%26%20Server-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Sockets](https://img.shields.io/badge/Networking-TCP%20Sockets-orange?style=flat-square)](https://en.wikipedia.org/wiki/Network_socket)
[![Windows](https://img.shields.io/badge/Platform-Windows-0078D6?style=flat-square&logo=windows&logoColor=white)](https://microsoft.com/windows)

---

## Descripción

AutoParking es un sistema de parqueadero distribuido que simula entradas y salidas de vehículos en tiempo real. Funciona sobre dos computadores en red local: uno corre el **simulador en C++** (cliente) que genera eventos de estacionamiento, y el otro corre el **visualizador en Python** (servidor) que recibe los datos y actualiza la interfaz gráfica.

La comunicación entre procesos se realiza vía **sockets TCP**, y la lógica C++ se expone a Python como una **DLL (Dynamic Link Library)** accedida con `ctypes`.

---

## Arquitectura del sistema

```
┌──────────────────────────────┐         TCP Socket         ┌─────────────────────────────────┐
│   Computador 1 — Simulador   │  ─────────────────────►   │  Computador 2 — Visualizador    │
│                              │                            │                                 │
│  autoparking.exe (C++)        │                            │  main.py (Python + Tkinter)     │
│  ├─ Generador de placas       │                            │  ├─ Servidor socket             │
│  ├─ Lógica de celdas          │                            │  ├─ Interfaz gráfica (grid)     │
│  ├─ Cliente socket            │                            │  ├─ Tabla de historial          │
│  └─ DLL wrapper               │                            │  └─ Puente ctypes ↔ DLL         │
└──────────────────────────────┘                            └─────────────────────────────────┘
```

---

## Stack tecnológico

| Componente | Tecnología |
|------------|-----------|
| Lógica de negocio | C++ (g++ / MinGW-w64) |
| Interfaz gráfica | Python 3 + Tkinter |
| Comunicación | TCP Sockets (C++ cliente · Python servidor) |
| Interoperabilidad | DLL + `ctypes` |
| Build automation | `compilar.bat` (Windows) |

---

## Estructura del proyecto

```
AutoParking/
└── parqueadero/
    ├── cpp/
    │   ├── autoparking.exe     # Ejecutable principal (generado al compilar)
    │   ├── libreria.dll        # DLL con lógica del parqueadero
    │   └── *.cpp / *.h         # Código fuente C++
    ├── python/
    │   ├── main.py             # Servidor + GUI Tkinter
    │   └── libreria.dll        # Copia de la DLL (copiada automáticamente por compilar.bat)
    └── compilar.bat            # Script de compilación y configuración
```

---

## Instalación y uso

### Requisitos

- **Computador 1 y 2** en la misma red WiFi o LAN
- **g++ (MinGW-w64)** instalado y en el PATH
- **Python 3.x** instalado en el sistema

### Paso 1: Compilar (cualquier computador)

```bat
compilar.bat
```

Genera `autoparking.exe` y `libreria.dll` en `cpp/`, y copia la DLL a `python/` automáticamente.

### Paso 2: Iniciar el Visualizador (Computador 2 — Servidor)

```bash
cd parqueadero/python/
python main.py
```

Anotar la IP del Computador 2 (`ipconfig` → dirección IPv4).

### Paso 3: Iniciar el Simulador (Computador 1 — Cliente)

```bash
cd parqueadero/cpp/
.\autoparking.exe
# Ingresar la IP del Computador 2 cuando se solicite
```

---

## Interfaz gráfica

La GUI muestra en tiempo real:

- **Grid de celdas** — 🟩 Verde = libre · 🟥 Rojo = ocupado
- **Tabla de historial** — últimos 50 eventos con Placa, Hora, Celda y tipo (Entrada / Salida)

---

## Características técnicas

- Generación automática de placas vehiculares (formato colombiano)
- Asignación y liberación dinámica de celdas
- Comunicación bidireccional vía sockets TCP en red local
- Interoperabilidad C++ ↔ Python mediante DLL compilada y `ctypes`
- Build automatizado para Windows con script `.bat`

---

## Autores

Proyecto desarrollado como trabajo académico en la Universidad de Antioquia.
