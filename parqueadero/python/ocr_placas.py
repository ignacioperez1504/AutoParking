"""
Módulo para detección y validación de placas vehiculares usando EasyOCR
"""
import re
import easyocr
import cv2
import numpy as np

class OCRPlacas:
    def __init__(self, idioma="es"):
        """Inicializa el lector OCR con EasyOCR"""
        print("[OCR] Inicializando EasyOCR...")
        self.reader = easyocr.Reader([idioma], gpu=False)
        print("[OCR] EasyOCR inicializado correctamente.")
    
    def validar_formato_placa(self, texto):
        """
        Valida que el texto tenga formato de placa: ABC123
        Acepta variaciones como:
        - ABC-123
        - ABC 123
        - ABC123
        """
        # Limpiar espacios y caracteres especiales
        texto_limpio = texto.upper().strip()
        
        # Remover espacios, guiones y otros caracteres especiales
        texto_limpio = re.sub(r'[\s\-\.\_]', '', texto_limpio)
        
        # Patrón: 3 letras + 3 números
        # Permite también variaciones como 2 letras + 4 números, etc.
        patron = r'^[A-Z]{2,3}\d{3,4}$'
        
        if re.match(patron, texto_limpio):
            return texto_limpio
        
        return None
    
    def detectar_placa_en_frame(self, frame):
        """
        Detecta texto en un frame usando OCR
        Retorna la placa validada o None
        """
        try:
            # Convertir a escala de grises para mejor OCR
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Aplicar CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # Detectar texto con EasyOCR
            resultados = self.reader.readtext(enhanced, detail=0)
            
            # Procesar cada texto detectado
            for texto in resultados:
                placa_validada = self.validar_formato_placa(texto)
                if placa_validada:
                    print(f"[OCR] Placa válida detectada: {placa_validada}")
                    return placa_validada
            
            return None
            
        except Exception as e:
            print(f"[ERROR OCR] {e}")
            return None
    
    def detectar_placa_con_confianza(self, frame, umbral_confianza=0.5):
        """
        Detecta placa con información de confianza
        Retorna (placa, confianza) o (None, 0)
        """
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # Detectar texto con detalles
            resultados = self.reader.readtext(enhanced)
            
            mejor_placa = None
            mejor_confianza = 0
            
            for (bbox, texto, confianza) in resultados:
                placa_validada = self.validar_formato_placa(texto)
                if placa_validada and confianza > mejor_confianza:
                    mejor_placa = placa_validada
                    mejor_confianza = confianza
            
            if mejor_confianza >= umbral_confianza:
                print(f"[OCR] Placa detectada: {mejor_placa} (confianza: {mejor_confianza:.2f})")
                return mejor_placa, mejor_confianza
            
            return None, 0
            
        except Exception as e:
            print(f"[ERROR OCR] {e}")
            return None, 0
