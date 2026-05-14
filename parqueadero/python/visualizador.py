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
            
            self.celdas_widgets[i] = {"frame": cell_frame, "placa": lbl_placa}

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
        # Insertar al principio de la tabla
        self.tabla.insert("", 0, values=(hora, placa, celda, estado))
        
        # Limitar a 50 eventos
        if len(self.tabla.get_children()) > 50:
            ultimo = self.tabla.get_children()[-1]
            self.tabla.delete(ultimo)
            
        # Actualizar la grilla visual al recibir un evento
        self.actualizar_grilla()

    def actualizar_grilla(self):
        # Obtener estado de la DLL: lista de 30 strings ("1" o "0")
        estados = self.bridge.obtener_estado_celdas()
        
        for i, estado_bit in enumerate(estados):
            if i >= 30: break
            
            widget = self.celdas_widgets[i]
            if estado_bit == "1":
                widget["frame"].configure(bg="#ffcccc") # Rojo suave
                widget["placa"].configure(text="OCUPADA", bg="#ffcccc", fg="#cc0000")
            else:
                widget["frame"].configure(bg="#ccffcc") # Verde suave
                widget["placa"].configure(text="LIBRE", bg="#ccffcc", fg="#006600")
