"""
Módulo para captura de video de cámara web y detección de placas
Usa threading para no bloquear la interfaz Tkinter
"""
import cv2
import threading
import time
from collections import deque
from ocr_placas import OCRPlacas

class GestorCamara:
    def __init__(self, callback_placa_detectada=None, resolucion=(640, 480), fps=15):
        """
        Inicializa el gestor de cámara
        
        Args:
            callback_placa_detectada: función que se llama cuando detecta placa válida
            resolucion: tupla (ancho, alto) del frame
            fps: frames por segundo objetivo
        """
        self.callback = callback_placa_detectada
        self.resolucion = resolucion
        self.fps = fps
        self.intervalo_frame = 1.0 / fps
        
        self.activo = False
        self.hilo_captura = None
        self.hilo_ocr = None
        
        self.captura = None
        self.frame_actual = None
        self.frame_lock = threading.Lock()
        
        # Cola de frames para OCR
        self.cola_frames = deque(maxlen=5)
        
        # Histórico de placas detectadas para evitar duplicados
        self.placas_recientes = deque(maxlen=10)
        
        try:
            self.ocr = OCRPlacas(idioma="es")
        except Exception as e:
            print(f"[ERROR CAMARA] No se pudo inicializar OCR: {e}")
            self.ocr = None
    
    def iniciar(self):
        """Inicia la captura de cámara y el procesamiento OCR"""
        if self.activo:
            print("[CAMARA] Ya está activa")
            return
        
        print("[CAMARA] Iniciando captura...")
        self.activo = True
        
        # Iniciar hilo de captura
        self.hilo_captura = threading.Thread(target=self._capturar_video, daemon=True)
        self.hilo_captura.start()
        
        # Iniciar hilo de OCR si está disponible
        if self.ocr:
            self.hilo_ocr = threading.Thread(target=self._procesar_ocr, daemon=True)
            self.hilo_ocr.start()
    
    def detener(self):
        """Detiene la captura de cámara"""
        print("[CAMARA] Deteniendo captura...")
        self.activo = False
        
        # Esperar a que terminen los hilos
        if self.hilo_captura:
            self.hilo_captura.join(timeout=2)
        if self.hilo_ocr:
            self.hilo_ocr.join(timeout=2)
        
        # Liberar recursos de OpenCV
        if self.captura:
            self.captura.release()
            self.captura = None
        
        print("[CAMARA] Captura detenida")
    
    def _capturar_video(self):
        """Hilo: Captura frames de la cámara web"""
        try:
            self.captura = cv2.VideoCapture(0)
            
            if not self.captura.isOpened():
                print("[ERROR CAMARA] No se pudo acceder a la cámara")
                self.activo = False
                return
            
            # Configurar resolución
            self.captura.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolucion[0])
            self.captura.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolucion[1])
            self.captura.set(cv2.CAP_PROP_FPS, self.fps)
            
            print("[CAMARA] Cámara inicializada correctamente")
            
            tiempo_ultimo_frame = time.time()
            
            while self.activo:
                ret, frame = self.captura.read()
                
                if not ret:
                    print("[ERROR CAMARA] No se pudo capturar frame")
                    break
                
                # Guardar frame actual para visualización
                with self.frame_lock:
                    self.frame_actual = frame.copy()
                
                # Agregar frame a la cola para OCR
                self.cola_frames.append(frame.copy())
                
                # Controlar FPS
                tiempo_actual = time.time()
                tiempo_espera = self.intervalo_frame - (tiempo_actual - tiempo_ultimo_frame)
                if tiempo_espera > 0:
                    time.sleep(tiempo_espera)
                tiempo_ultimo_frame = time.time()
        
        except Exception as e:
            print(f"[ERROR CAMARA] Excepción en captura: {e}")
        finally:
            if self.captura:
                self.captura.release()
    
    def _procesar_ocr(self):
        """Hilo: Procesa frames con OCR para detectar placas"""
        if not self.ocr:
            return
        
        tiempo_ultimo_ocr = time.time()
        intervalo_ocr = 0.5  # Procesar cada 0.5 segundos como máximo
        
        while self.activo:
            try:
                # Procesar solo si ha pasado suficiente tiempo
                tiempo_actual = time.time()
                if tiempo_actual - tiempo_ultimo_ocr < intervalo_ocr:
                    time.sleep(0.1)
                    continue
                
                # Obtener un frame de la cola
                if len(self.cola_frames) == 0:
                    time.sleep(0.1)
                    continue
                
                frame = self.cola_frames[-1]  # Usar el más reciente
                
                # Detectar placa
                placa, confianza = self.ocr.detectar_placa_con_confianza(frame, umbral_confianza=0.4)
                
                if placa:
                    # Evitar duplicados (misma placa en menos de 3 segundos)
                    es_duplicado = False
                    if placa in self.placas_recientes:
                        es_duplicado = True
                    
                    if not es_duplicado:
                        self.placas_recientes.append(placa)
                        print(f"[CAMARA] Nueva placa detectada: {placa}")
                        
                        # Llamar callback si existe
                        if self.callback:
                            self.callback(placa, frame)
                
                tiempo_ultimo_ocr = tiempo_actual
            
            except Exception as e:
                print(f"[ERROR OCR] {e}")
                time.sleep(0.5)
    
    def obtener_frame_actual(self):
        """Obtiene el frame actual para visualización"""
        with self.frame_lock:
            if self.frame_actual is not None:
                return self.frame_actual.copy()
        return None
    
    def limpiar_historico_placas(self):
        """Limpia el histórico de placas detectadas"""
        self.placas_recientes.clear()
