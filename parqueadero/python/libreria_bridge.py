import ctypes
import os

class LibreriaBridge:
    def __init__(self):
        # La DLL sera copiada a esta misma carpeta por el script de compilacion
        dll_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "libreria.dll"))
        
        # Si no esta en la carpeta local, intentar en la carpeta cpp (por si acaso)
        if not os.path.exists(dll_path):
            dll_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cpp", "libreria.dll"))
        
        try:
            self.lib = ctypes.CDLL(dll_path)
        except Exception as e:
            print(f"Error al cargar la DLL en {dll_path}: {e}")
            raise

        # Configurar tipos de argumentos y retornos
        self.lib.inicializar.argtypes = []
        self.lib.inicializar.restype = None

        self.lib.procesarPlaca.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.lib.procesarPlaca.restype = None

        self.lib.obtenerEstadoCeldas.argtypes = [ctypes.c_char_p]
        self.lib.obtenerEstadoCeldas.restype = None

    def inicializar(self):
        self.lib.inicializar()

    def procesar_placa(self, placa):
        # Buffer para recibir el resultado "CELDA|HORA|ESTADO"
        resultado_buffer = ctypes.create_string_buffer(100)
        self.lib.procesarPlaca(placa.encode('utf-8'), resultado_buffer)
        
        # Parsear el resultado
        res_str = resultado_buffer.value.decode('utf-8')
        if res_str == "LLENO|0|ERROR":
            return {"error": "Lleno"}
        
        partes = res_str.split('|')
        return {
            "celda": partes[0],
            "hora": partes[1],
            "estado": partes[2]
        }

    def obtener_estado_celdas(self):
        # Buffer para recibir "1,0,1,..." (30 celdas + comas = aprox 60 chars)
        buffer = ctypes.create_string_buffer(200)
        self.lib.obtenerEstadoCeldas(buffer)
        
        res_str = buffer.value.decode('utf-8')
        if not res_str:
            return ["0"] * 30
            
        return res_str.split(',')
