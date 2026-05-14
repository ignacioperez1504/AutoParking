import socket
import threading

class SocketServidor:
    def __init__(self, host="0.0.0.0", puerto=5000):
        self.host = host
        self.puerto = puerto
        self.callback = None
        self.running = False

    def iniciar(self, callback_evento):
        self.callback = callback_evento
        self.running = True
        # Iniciar el servidor en un hilo separado
        hilo = threading.Thread(target=self._escuchar, daemon=True)
        hilo.start()
        print(f"[SERVIDOR] Escuchando en {self.host}:{self.puerto}...")

    def _escuchar(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
            # Reutilizar puerto para evitar errores de 'Address already in use'
            servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            servidor.bind((self.host, self.puerto))
            servidor.listen(5)

            while self.running:
                conn, addr = servidor.accept()
                with conn:
                    # print(f"[SERVIDOR] Conexion recibida de {addr}")
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        
                        # Mensaje esperado: "PLACA|HORA|CELDA|ESTADO"
                        mensaje = data.decode('utf-8')
                        partes = mensaje.split('|')
                        
                        if len(partes) == 4:
                            placa, hora, celda, estado = partes
                            # Notificar al visualizador a traves del callback
                            if self.callback:
                                self.callback(placa, hora, celda, estado)
                        else:
                            print(f"[ERROR] Mensaje mal formado: {mensaje}")

    def detener(self):
        self.running = False
