import tkinter as tk
from tkinter import ttk

class Visualizador:
    def __init__(self, root, bridge):
        self.root = root
        self.bridge = bridge
        self.root.title("Sistema de Parqueadero — En vivo")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        # Diccionario para guardar los widgets de las celdas
        self.celdas_widgets = {}
        
        self._setup_ui()
        self.actualizar_grilla()

    def _setup_ui(self):
        # --- PARTE SUPERIOR: GRILLA DE CELDAS ---
        frame_grilla = tk.LabelFrame(self.root, text="Estado de Celdas (30)", padx=10, pady=10, bg="#f0f0f0", font=("Arial", 12, "bold"))
        frame_grilla.pack(fill="x", padx=20, pady=10)

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

        # --- PARTE INFERIOR: TABLA DE HISTORIAL ---
        frame_historial = tk.LabelFrame(self.root, text="Historial de Eventos", padx=10, pady=10, bg="#f0f0f0", font=("Arial", 12, "bold"))
        frame_historial.pack(fill="both", expand=True, padx=20, pady=10)

        columnas = ("hora", "placa", "celda", "estado")
        self.tabla = ttk.Treeview(frame_historial, columns=columnas, show="headings", height=10)
        
        self.tabla.heading("hora", text="Hora")
        self.tabla.heading("placa", text="Placa")
        self.tabla.heading("celda", text="Celda")
        self.tabla.heading("estado", text="Estado")

        self.tabla.column("hora", width=100, anchor="center")
        self.tabla.column("placa", width=150, anchor="center")
        self.tabla.column("celda", width=100, anchor="center")
        self.tabla.column("estado", width=150, anchor="center")

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame_historial, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)
        
        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def agregar_evento(self, placa, hora, celda, estado):
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
