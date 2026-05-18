# AutoParking — Sistema de Gestión de Parqueadero Multi-Lenguaje

Este proyecto es un sistema de parqueadero distribuido que utiliza **C++** para la lógica de bajo nivel y simulación, y **Python** para la interfaz gráfica y servidor de datos. Ahora incluye **reconocimiento de placas por cámara** usando OpenCV y EasyOCR.

## Requisitos
*   **Compilador C++**: g++ (MinGW-w64) instalado en el PATH.
*   **Python 3.x**: Instalado en el sistema.
*   **Red**: Ambos computadores deben estar en la misma red WiFi o local.
*   **Cámara Web**: Opcional, para modo de reconocimiento de placas.
*   **Dependencias Python**: Ver sección "Instalación de Dependencias".

---

## Instalación de Dependencias Python

Antes de ejecutar el visualizador, instala las dependencias requeridas:

```bash
pip install opencv-python easyocr pillow
```

Si ya tienes un `requirements.txt`, puedes usar:

```bash
pip install -r requirements.txt
```

---

## Guía de Configuración

### Paso 1: Compilación (En cualquier computador)
1.  Abre la carpeta raíz del proyecto.
2.  Haz doble clic en el archivo `compilar.bat`.
3.  Esto generará `autoparking.exe` y `libreria.dll` dentro de la carpeta `cpp/`, y copiará la DLL automáticamente a la carpeta `python/`.

### Paso 2: Ejecutar el Visualizador (Computador 2 - Servidor)
Este computador actuará como el servidor que recibe los datos y muestra la interfaz.
1.  Abre una terminal en la carpeta `parqueadero/python/`.
2.  Instala las dependencias (si aún no lo has hecho):
    ```bash
    pip install opencv-python easyocr pillow
    ```
3.  Ejecuta el comando:
    ```bash
    python main.py
    ```
4.  Anota la dirección IP de este computador. Para verla en Windows, abre una terminal y escribe:
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

## Características Nuevas: Modo Cámara

### Botones de Modo
La interfaz ahora tiene dos botones en la parte superior:
*   **Aleatorio**: Modo original con generación aleatoria de placas y asignación automática de celdas.
*   **Cámara**: Activa la cámara web para reconocimiento de placas en vivo.

### Modo Cámara
1.  Haz clic en el botón "Cámara" en la interfaz.
2.  La cámara web se iniciará automáticamente.
3.  El sistema detectará placas vehiculares usando OCR (EasyOCR).
4.  Cuando detecte una placa válida:
    - Se mostrará un diálogo preguntando: **¿Entrada o Salida?**
    - Si es **ENTRADA**: Se asigna automáticamente una celda libre.
    - Si es **SALIDA**: Se libera la celda ocupada por ese vehículo.
5.  La captura se guardará en la carpeta `capturas/PLACA.jpg`.

### Modo Aleatorio (Mejorado)
*   Ahora registra automáticamente las horas de entrada y salida.
*   Se muestra un **gráfico de afluencia horaria** en tiempo real.
*   El gráfico es persistente y se guarda en `estadisticas.json`.

---

## Interfaz Gráfica (Visualizador)
*   **Celda en VERDE**: La celda está libre.
*   **Celda en ROJO**: La celda está ocupada por un vehículo.
*   **Historial**: Tabla que muestra los últimos 50 eventos (Placa, Hora, Celda y Estado).
*   **Gráfico de Afluencia**: Muestra entradas (azul) y salidas (rojo) por hora.
*   **Vista de Cámara**: Muestra el video en vivo cuando el modo cámara está activo.

## Archivos Nuevos
*   `python/camara.py`: Módulo de captura de cámara web con threading.
*   `python/ocr_placas.py`: Módulo de detección y validación de placas usando EasyOCR.
*   `capturas/`: Carpeta donde se guardan las capturas de placas detectadas.
*   `estadisticas.json`: Archivo que almacena el histórico de afluencia.

## Estructura del Proyecto
*   `cpp/`: Lógica del parqueadero, generador de placas, cliente socket y wrapper de DLL.
*   `python/`: Servidor socket, interfaz gráfica (Tkinter), cámara y puente con la DLL (ctypes).
*   `compilar.bat`: Automatización de construcción para Windows.
