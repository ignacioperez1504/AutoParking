# AutoParking — Sistema de Gestión de Parqueadero Multi-Lenguaje

Este proyecto es un sistema de parqueadero distribuido que utiliza **C++** para la lógica de bajo nivel y simulación, y **Python** para la interfaz gráfica y servidor de datos.

## Requisitos
*   **Compilador C++**: g++ (MinGW-w64) instalado en el PATH.
*   **Python 3.x**: Instalado en el sistema.
*   **Red**: Ambos computadores deben estar en la misma red WiFi o local.

---

## Guía de Configuración

### Paso 1: Compilación (En cualquier computador)
1.  Abre la carpeta raíz del proyecto.
2.  Haz doble clic en el archivo `compilar.bat`.
3.  Esto generará `autoparking.exe` y `libreria.dll` dentro de la carpeta `cpp/`, y copiará la DLL automáticamente a la carpeta `python/`.

### Paso 2: Ejecutar el Visualizador (Computador 2 - Servidor)
Este computador actuará como el servidor que recibe los datos y muestra la interfaz.
1.  Abre una terminal en la carpeta `parqueadero/python/`.
2.  Ejecuta el comando:
    ```bash
    python main.py
    ```
3.  Anota la dirección IP de este computador. Para verla en Windows, abre una terminal y escribe:
    ```cmd
    ipconfig
    ```
    Busca la dirección "IPv4" (ejemplo: `192.168.1.15`).

### Paso 3: Ejecutar el Simulador (Computador 1 - Cliente)
Este computador generará los ingresos y salidas de vehículos.
1.  Abre una terminal en la carpeta `parqueadero/cpp/`.
2.  Ejecuta el programa:
    ```cmd
    .\autoparking.exe
    ```
3.  Cuando el programa pregunte, ingresa la IP del Computador 2 obtenida en el paso anterior.

---

## Interfaz Gráfica (Visualizador)
*   **Celda en VERDE**: La celda está libre.
*   **Celda en ROJO**: La celda está ocupada por un vehículo.
*   **Historial**: La tabla inferior muestra los últimos 50 eventos (Placa, Hora, Celda y si fue Entrada o Salida).

## Estructura del Proyecto
*   `cpp/`: Lógica del parqueadero, generador de placas, cliente socket y wrapper de DLL.
*   `python/`: Servidor socket, interfaz gráfica (Tkinter) y puente con la DLL (ctypes).
*   `compilar.bat`: Automatización de construcción para Windows.
