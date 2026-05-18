import tkinter as tk
from socket_servidor import SocketServidor
from libreria_bridge import LibreriaBridge
from visualizador import Visualizador
from camara import GestorCamara

def main():
    print("--- INICIANDO SISTEMA DE PARQUEADERO (SERVIDOR PYTHON) ---")
    
    # 1. Inicializar la conexion con la DLL de C++
    try:
        bridge = LibreriaBridge()
        bridge.inicializar()
        print("[BRIDGE] DLL de C++ cargada e inicializada correctamente.")
    except Exception as e:
        print(f"[ERROR] No se pudo inicializar la DLL: {e}")
        return

    # 2. Inicializar gestor de cámara
    gestor_camara = None
    try:
        gestor_camara = GestorCamara(resolucion=(640, 480), fps=15)
        print("[CAMARA] Gestor de cámara inicializado.")
    except Exception as e:
        print(f"[ERROR] No se pudo inicializar cámara: {e}")

    # 3. Crear la ventana principal de Tkinter
    root = tk.Tk()
    app = Visualizador(root, bridge, gestor_camara)
    
    # Configurar callback de placa detectada en gestor de cámara
    if gestor_camara:
        gestor_camara.callback = lambda placa, frame: root.after(
            0, app.manejar_placa_detectada, placa, frame
        )

    # 4. Definir que hacer cuando llegue un mensaje por socket
    def callback_nuevo_mensaje(placa, hora, celda, estado):
        # Esta funcion corre en el hilo del socket.
        # Para actualizar la UI de Tkinter de forma segura, usamos root.after()
        root.after(0, app.agregar_evento, placa, hora, celda, estado)

    # 5. Iniciar el servidor socket
    servidor = SocketServidor()
    servidor.iniciar(callback_nuevo_mensaje)

    # 6. Loop principal de la interfaz
    try:
        root.mainloop()
    finally:
        # Limpieza al cerrar
        print("Cerrando servidor...")
        servidor.detener()
        
        if gestor_camara and gestor_camara.activo:
            print("Deteniendo cámara...")
            gestor_camara.detener()

if __name__ == "__main__":
    main()
