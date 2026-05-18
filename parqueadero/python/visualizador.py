import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import cv2
import threading
import os
import datetime
from collections import defaultdict
import json

class Visualizador:
    def __init__(self, root, bridge, gestor_camara=None):
        self.root = root
        self.bridge = bridge
        self.gestor_camara = gestor_camara
        
        self.root.title("Sistema de Parqueadero — En vivo")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")

        # Diccionario para guardar los widgets de las celdas
        self.celdas_widgets = {}
        
        # Control de modo
        self.modo_actual = "aleatorio"  # "aleatorio" o "camara"
        self.camara_activa = False
        
        # Histórico de eventos para gráfico
        self.eventos_por_hora = defaultdict(lambda: {"entrada": 0, "salida": 0})
        self.cargar_estadisticas()
        
        # Mapa de placas a celdas para manejo de salidas
        self.placas_a_celdas = {}
        
        # Variable para almacenar frame capturado para guardar
        self.frame_capturado_actual = None
        
        # ID del evento pendiente (para evitar duplicados)
        self.evento_pendiente_id = None

        # Control de captura manual
        self.esperando_captura = False
        
        self._setup_ui()
        self.actualizar_grilla()
        
        # Actualizar vista de cámara si está activa
        if self.gestor_camara:
            self._actualizar_vista_camara()
    
    def _setup_ui(self):
        # --- FRAME SUPERIOR: CONTROLES ---
        frame_controles = tk.Frame(self.root, bg="#2c3e50", height=60)
        frame_controles.pack(fill="x", padx=0, pady=0)
        
        lbl_titulo = tk.Label(frame_controles, text="Sistema de Parqueadero", font=("Arial", 14, "bold"), 
                             bg="#2c3e50", fg="white")
        lbl_titulo.pack(side="left", padx=20, pady=10)
        
        btn_captura = tk.Button(
            frame_controles,
            text="Iniciar Captura",
            command=self._iniciar_captura_manual
        )
        btn_captura.pack(side="left", padx=5, pady=10)


        # Botones de modo
        btn_aleatorio = tk.Button(frame_controles, text="Aleatorio", width=12, bg="#3498db", 
                                 fg="white", font=("Arial", 10, "bold"), 
                                 command=self._cambiar_modo_aleatorio)
        btn_aleatorio.pack(side="left", padx=5, pady=10)
        self.btn_aleatorio = btn_aleatorio
        
        btn_camara = tk.Button(frame_controles, text="Cámara", width=12, bg="#95a5a6", 
                              fg="white", font=("Arial", 10, "bold"), 
                              command=self._cambiar_modo_camara)
        btn_camara.pack(side="left", padx=5, pady=10)
        self.btn_camara = btn_camara
        
        # Etiqueta de modo actual
        self.lbl_modo = tk.Label(frame_controles, text="Modo: ALEATORIO", font=("Arial", 10, "bold"), 
                                bg="#2c3e50", fg="#2ecc71")
        self.lbl_modo.pack(side="left", padx=20, pady=10)
        
        # --- FRAME PRINCIPAL: DOS COLUMNAS ---
        frame_main = tk.Frame(self.root, bg="#f0f0f0")
        frame_main.pack(fill="both", expand=True, padx=10, pady=10)
        
        # COLUMNA IZQUIERDA: GRILLA Y CÁMARA
        frame_left = tk.Frame(frame_main, bg="#f0f0f0")
        frame_left.pack(side="left", fill="both", expand=True, padx=5)
        
        # --- GRILLA DE CELDAS ---
        frame_grilla = tk.LabelFrame(frame_left, text="Estado de Celdas (30)", padx=10, pady=10, 
                                     bg="#f0f0f0", font=("Arial", 12, "bold"))
        frame_grilla.pack(fill="x", padx=0, pady=5)

        # Crear grilla 5x6
        for i in range(30):
            fila = i // 5
            col = i % 5
            
            cell_frame = tk.Frame(frame_grilla, width=140, height=50, bd=2, relief="groove")
            cell_frame.grid(row=fila, column=col, padx=5, pady=5)
            cell_frame.pack_propagate(False)
            
            lbl_num = tk.Label(cell_frame, text=f"Celda {i+1}", font=("Arial", 8, "bold"))
            lbl_num.pack()
            
            lbl_placa = tk.Label(cell_frame, text="LIBRE", font=("Arial", 9))
            lbl_placa.pack()
            
            # Guardamos referencias para actualizar luego
            self.celdas_widgets[i] = {
                "frame": cell_frame, 
                "placa_label": lbl_placa,
                "num_label": lbl_num
            }

        # --- VISTA DE CÁMARA ---
        self.frame_camara_container = tk.LabelFrame(frame_left, text="Vista de Cámara", padx=5, pady=5, 
                                                    bg="#f0f0f0", font=("Arial", 10, "bold"))
        self.frame_camara_container.pack(fill="both", expand=True, padx=0, pady=5)
        
        self.canvas_camara = tk.Canvas(self.frame_camara_container, width=400, height=300, bg="black")
        self.canvas_camara.pack(fill="both", expand=True)
        
        # COLUMNA DERECHA: HISTORIAL Y GRÁFICO
        frame_right = tk.Frame(frame_main, bg="#f0f0f0")
        frame_right.pack(side="right", fill="both", expand=True, padx=5)
        
        # --- TABLA DE HISTORIAL ---
        frame_historial = tk.LabelFrame(frame_right, text="Historial de Eventos", padx=10, pady=10, 
                                        bg="#f0f0f0", font=("Arial", 12, "bold"))
        frame_historial.pack(fill="both", expand=True, padx=0, pady=5)

        columnas = ("hora", "placa", "celda", "estado")
        self.tabla = ttk.Treeview(frame_historial, columns=columnas, show="headings", height=15)
        
        self.tabla.heading("hora", text="Hora")
        self.tabla.heading("placa", text="Placa")
        self.tabla.heading("celda", text="Celda")
        self.tabla.heading("estado", text="Estado")

        self.tabla.column("hora", width=80, anchor="center")
        self.tabla.column("placa", width=100, anchor="center")
        self.tabla.column("celda", width=80, anchor="center")
        self.tabla.column("estado", width=100, anchor="center")

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame_historial, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)
        
        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # --- GRÁFICO DE AFLUENCIA ---
        frame_grafico = tk.LabelFrame(frame_right, text="Afluencia Horaria", padx=10, pady=10, 
                                      bg="#f0f0f0", font=("Arial", 12, "bold"))
        frame_grafico.pack(fill="x", padx=0, pady=5)
        
        self.canvas_grafico = tk.Canvas(frame_grafico, width=300, height=150, bg="white", relief="groove", bd=1)
        self.canvas_grafico.pack(fill="both", expand=True)
        self.dibujar_grafico()
    
    def _iniciar_captura_manual(self):
        """Activa una única detección de placa"""
        
        if self.modo_actual != "camara":
            messagebox.showwarning(
                "Aviso",
                "Debes activar el modo cámara primero"
            )
            return

        # LIMPIAR HISTÓRICO PARA PODER LEER LA MISMA PLACA OTRA VEZ
        if self.gestor_camara:
            self.gestor_camara.limpiar_historico_placas()

        self.esperando_captura = True
        
        print("[VISUALIZADOR] Esperando captura de placa...")
        
        messagebox.showinfo(
            "Captura",
            "Apunta la cámara hacia la placa"
        )


    def _cambiar_modo_aleatorio(self):
        """Cambia al modo aleatorio"""
        if self.modo_actual == "aleatorio":
            return
        
        print("[VISUALIZADOR] Cambiando a modo ALEATORIO")
        self.modo_actual = "aleatorio"
        self.camara_activa = False
        
        # Detener cámara si está activa
        if self.gestor_camara:
            self.gestor_camara.detener()
        
        # Actualizar botones
        self.btn_aleatorio.configure(bg="#3498db")
        self.btn_camara.configure(bg="#95a5a6")
        self.lbl_modo.configure(text="Modo: ALEATORIO", fg="#2ecc71")
        
        # Limpiar canvas de cámara
        self.canvas_camara.delete("all")
        self.canvas_camara.create_text(200, 150, text="Modo: ALEATORIO", font=("Arial", 14), fill="gray")
    
    def _cambiar_modo_camara(self):
        """Cambia al modo cámara"""
        if self.modo_actual == "camara":
            return
        
        if not self.gestor_camara:
            messagebox.showerror("Error", "Cámara no disponible")
            return
        
        print("[VISUALIZADOR] Cambiando a modo CÁMARA")
        self.modo_actual = "camara"
        self.camara_activa = True
        
        # Iniciar cámara
        self.gestor_camara.iniciar()
        
        # Actualizar botones
        self.btn_aleatorio.configure(bg="#95a5a6")
        self.btn_camara.configure(bg="#3498db")
        self.lbl_modo.configure(text="Modo: CÁMARA", fg="#e74c3c")
    
    def _actualizar_vista_camara(self):
        """Actualiza la vista de cámara en el canvas"""
        if not self.camara_activa or not self.gestor_camara:
            self.root.after(100, self._actualizar_vista_camara)
            return
        
        frame = self.gestor_camara.obtener_frame_actual()
        
        if frame is not None:
            # Redimensionar frame para que quepa en el canvas
            altura, ancho = frame.shape[:2]
            escala = min(400 / ancho, 300 / altura)
            nuevo_ancho = int(ancho * escala)
            nueva_altura = int(altura * escala)
            
            frame_redimensionado = cv2.resize(frame, (nuevo_ancho, nueva_altura))
            
            # Convertir BGR a RGB para Tkinter
            frame_rgb = cv2.cvtColor(frame_redimensionado, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            
            # Convertir a PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Mostrar en canvas
            self.canvas_camara.delete("all")
            self.canvas_camara.create_image(200, 150, image=photo)
            self.canvas_camara.image = photo  # Mantener referencia
        
        # Programar siguiente actualización
        self.root.after(100, self._actualizar_vista_camara)
    
    def manejar_placa_detectada(self, placa, frame):
        if not self.esperando_captura:
            return

        """Maneja una placa detectada por la cámara"""
        print(f"[VISUALIZADOR] Placa detectada: {placa}")
        
        # Guardar frame capturado
        self.frame_capturado_actual = frame.copy()

        self.esperando_captura = False
        
        # Mostrar diálogo para elegir entrada/salida
        root_dialog = tk.Tk()
        root_dialog.withdraw()
        root_dialog.attributes('-topmost', True)
        
        resultado = messagebox.askyesno(
            "Placa Detectada",
            f"Placa: {placa}\n\n¿Entrada o Salida?\n\nSí = ENTRADA\nNo = SALIDA",
            parent=self.root
        )
        
        if resultado is None:
            # Cancelado
            return
        
        if resultado:
            # ENTRADA
            self._procesar_entrada_camara(placa)
        else:
            # SALIDA
            self._procesar_salida_camara(placa)
        
        root_dialog.destroy()
    
    def _procesar_entrada_camara(self, placa):
        """Procesa entrada de vehículo por cámara"""
        print(f"[ENTRADA] Procesando entrada de {placa}")
        
        try:
            # Procesar placa en la DLL de C++
            resultado = self.bridge.procesar_placa(placa)
            
            if "error" in resultado:
                messagebox.showerror("Error", f"Parqueadero lleno: {resultado['error']}")
                return
            
            celda = resultado["celda"]
            hora = resultado["hora"]
            estado = "ENTRADA"
            
            # Guardar mapping placa -> celda
            self.placas_a_celdas[placa] = int(celda)
            
            # Guardar captura
            self._guardar_captura(placa)
            
            # Agregar evento
            self.agregar_evento(placa, hora, celda, estado)
            
            # Actualizar estadísticas
            self._registrar_evento(estado)
            
            messagebox.showinfo("Éxito", f"Entrada registrada\nPlaca: {placa}\nCelda: {celda}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar entrada: {e}")
    
    def _procesar_salida_camara(self, placa):
        """Procesa salida de vehículo por cámara"""
        print(f"[SALIDA] Procesando salida de {placa}")
        
        try:
            # Buscar la celda ocupada por esta placa
            if placa in self.placas_a_celdas:
                celda = self.placas_a_celdas[placa]
                del self.placas_a_celdas[placa]
                
                # Simular salida: buscar en la DLL si existe registro
                # Por ahora registramos la salida directamente
                hora = datetime.datetime.now().strftime("%H:%M:%S")
                estado = "SALIDA"
                
                # Guardar captura
                self._guardar_captura(placa)
                
                # Agregar evento
                self.agregar_evento(placa, hora, str(celda), estado)
                
                # Actualizar estadísticas
                self._registrar_evento(estado)
                
                messagebox.showinfo("Éxito", f"Salida registrada\nPlaca: {placa}\nCelda: {celda}")
            else:
                messagebox.showwarning("Aviso", f"Placa {placa} no encontrada en el sistema")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar salida: {e}")
    
    def _guardar_captura(self, placa):
        """Guarda la captura de la placa"""
        if self.frame_capturado_actual is None:
            return
        
        try:
            # Crear directorio si no existe
            dir_capturas = os.path.join(os.path.dirname(__file__), "..", "capturas")
            os.makedirs(dir_capturas, exist_ok=True)
            
            # Guardar imagen
            ruta_captura = os.path.join(dir_capturas, f"{placa}.jpg")
            cv2.imwrite(ruta_captura, self.frame_capturado_actual)
            
            print(f"[CAPTURA] Guardada: {ruta_captura}")
        
        except Exception as e:
            print(f"[ERROR] No se pudo guardar captura: {e}")
    
    def _registrar_evento(self, estado):
        """Registra un evento en las estadísticas"""
        hora_actual = datetime.datetime.now().hour
        if estado == "ENTRADA":
            self.eventos_por_hora[hora_actual]["entrada"] += 1
        elif estado == "SALIDA":
            self.eventos_por_hora[hora_actual]["salida"] += 1
        
        # Guardar estadísticas
        self.guardar_estadisticas()
        self.dibujar_grafico()
    
    def dibujar_grafico(self):
        """Dibuja el gráfico de afluencia horaria"""
        self.canvas_grafico.delete("all")
        
        if not self.eventos_por_hora:
            self.canvas_grafico.create_text(150, 75, text="Sin datos", font=("Arial", 10), fill="gray")
            return
        
        # Configuración del gráfico
        ancho = 300
        alto = 150
        margen = 20
        area_ancho = ancho - 2 * margen
        area_alto = alto - 2 * margen
        
        # Encontrar máximo
        max_valor = max(
            max(datos["entrada"], datos["salida"]) 
            for datos in self.eventos_por_hora.values()
        ) if self.eventos_por_hora else 1
        
        if max_valor == 0:
            max_valor = 1
        
        # Dibujar marco
        self.canvas_grafico.create_rectangle(margen, margen, ancho - margen, alto - margen, 
                                           outline="black", width=1)
        
        # Dibujar barras
        horas_activas = sorted(self.eventos_por_hora.keys())
        num_horas = len(horas_activas)
        
        if num_horas > 0:
            ancho_barra = area_ancho / (num_horas * 2.5)
            
            for idx, hora in enumerate(horas_activas):
                datos = self.eventos_por_hora[hora]
                entrada = datos["entrada"]
                salida = datos["salida"]
                
                x_base = margen + (idx * 2.5 + 0.5) * ancho_barra
                
                # Barra de entrada (azul)
                altura_entrada = (entrada / max_valor) * area_alto
                self.canvas_grafico.create_rectangle(
                    x_base, alto - margen - altura_entrada,
                    x_base + ancho_barra * 0.8, alto - margen,
                    fill="#3498db", outline="black", width=1
                )
                
                # Barra de salida (roja)
                x_salida = x_base + ancho_barra * 0.9
                altura_salida = (salida / max_valor) * area_alto
                self.canvas_grafico.create_rectangle(
                    x_salida, alto - margen - altura_salida,
                    x_salida + ancho_barra * 0.8, alto - margen,
                    fill="#e74c3c", outline="black", width=1
                )
                
                # Etiqueta de hora
                self.canvas_grafico.create_text(
                    x_base + ancho_barra, alto - margen + 10,
                    text=f"{hora}h", font=("Arial", 7)
                )
        
        # Leyenda
        self.canvas_grafico.create_rectangle(margen, margen, margen + 10, margen + 10, 
                                           fill="#3498db", outline="black")
        self.canvas_grafico.create_text(margen + 20, margen + 5, text="Entrada", 
                                       font=("Arial", 8), anchor="w")
        
        self.canvas_grafico.create_rectangle(margen + 80, margen, margen + 90, margen + 10, 
                                           fill="#e74c3c", outline="black")
        self.canvas_grafico.create_text(margen + 100, margen + 5, text="Salida", 
                                       font=("Arial", 8), anchor="w")
    
    def cargar_estadisticas(self):
        """Carga las estadísticas guardadas"""
        try:
            stats_file = os.path.join(os.path.dirname(__file__), "..", "estadisticas.json")
            if os.path.exists(stats_file):
                with open(stats_file, 'r') as f:
                    datos = json.load(f)
                    self.eventos_por_hora = defaultdict(lambda: {"entrada": 0, "salida": 0})
                    for hora_str, valores in datos.items():
                        self.eventos_por_hora[int(hora_str)] = valores
        except Exception as e:
            print(f"[ERROR] No se pudieron cargar estadísticas: {e}")
    
    def guardar_estadisticas(self):
        """Guarda las estadísticas en un archivo JSON"""
        try:
            stats_file = os.path.join(os.path.dirname(__file__), "..", "estadisticas.json")
            datos = {str(hora): valores for hora, valores in self.eventos_por_hora.items()}
            with open(stats_file, 'w') as f:
                json.dump(datos, f, indent=2)
        except Exception as e:
            print(f"[ERROR] No se pudieron guardar estadísticas: {e}")
    
    def agregar_evento(self, placa, hora, celda, estado):
        """Agrega un evento a la tabla de historial y actualiza la grilla"""
        # 1. Insertar en la tabla de historial
        self.tabla.insert("", 0, values=(hora, placa, celda, estado))
        
        # Limitar a 50 eventos
        if len(self.tabla.get_children()) > 50:
            ultimo = self.tabla.get_children()[-1]
            self.tabla.delete(ultimo)
            
        # 2. Actualizar la celda individual directamente usando los datos del mensaje
        try:
            # Convertir numero de celda (1-30) a indice (0-29)
            idx = int(celda) - 1
            
            if 0 <= idx < 30:
                widget = self.celdas_widgets[idx]
                
                if estado == "ENTRADA":
                    # Poner en ROJO y mostrar placa
                    widget["frame"].configure(bg="#ff4444")
                    widget["placa_label"].configure(text=placa, bg="#ff4444", fg="white", font=("Arial", 9, "bold"))
                    widget["num_label"].configure(bg="#ff4444", fg="white")
                else:
                    # Poner en VERDE y mostrar LIBRE
                    widget["frame"].configure(bg="#2ecc71")
                    widget["placa_label"].configure(text="LIBRE", bg="#2ecc71", fg="white", font=("Arial", 9))
                    widget["num_label"].configure(bg="#2ecc71", fg="white")
        except ValueError:
            pass # Celda invalida (ej: "-1" si esta lleno)

    def actualizar_grilla(self):
        """Sincroniza toda la grilla con el estado real de la DLL (usado al inicio)"""
        estados = self.bridge.obtener_estado_celdas()
        
        for i, estado_bit in enumerate(estados):
            if i >= 30: break
            
            widget = self.celdas_widgets[i]
            if estado_bit == "1":
                widget["frame"].configure(bg="#ff4444")
                widget["placa_label"].configure(text="OCUPADA", bg="#ff4444", fg="white")
                widget["num_label"].configure(bg="#ff4444", fg="white")
            else:
                widget["frame"].configure(bg="#2ecc71")
                widget["placa_label"].configure(text="LIBRE", bg="#2ecc71", fg="white")
                widget["num_label"].configure(bg="#2ecc71", fg="white")
