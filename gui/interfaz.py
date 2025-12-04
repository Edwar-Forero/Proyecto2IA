import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from PIL import Image, ImageTk
import os

class InterfazYuGiOh:
    """Interfaz gráfica principal del juego"""
    
    def __init__(self, root, juego):
        self.root = root
        self.juego = juego
        self.root.title("Yu-Gi-Oh! Forbidden Memories - Minimax AI")
        self.root.geometry("1400x900")
        self.root.configure(bg="#2c3e50")
        
        # Variables para selección
        self.carta_seleccionada = None
        self.modo_seleccion = None  # "atacar", "fusionar", None
        self.carta_fusion_1 = None
        
        # Cache de imágenes
        self.imagenes_cache = {}
        
        self.crear_interfaz()
        self.actualizar_interfaz()
    
    def crear_interfaz(self):
        """Crea todos los componentes de la interfaz"""
        
        # Frame superior - Campo de la IA
        frame_ia = tk.Frame(self.root, bg="#34495e", relief=tk.RAISED, bd=2)
        frame_ia.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
        
        # Info IA
        info_ia = tk.Frame(frame_ia, bg="#34495e")
        info_ia.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        self.label_ia_nombre = tk.Label(info_ia, text="IA", font=("Arial", 16, "bold"), 
                                         bg="#34495e", fg="#e74c3c")
        self.label_ia_nombre.pack(side=tk.LEFT, padx=10)
        
        self.label_ia_vida = tk.Label(info_ia, text="LP: 8000", font=("Arial", 14), 
                                       bg="#34495e", fg="#ecf0f1")
        self.label_ia_vida.pack(side=tk.LEFT, padx=10)
        
        self.label_ia_deck = tk.Label(info_ia, text="Deck: 15", font=("Arial", 12), 
                                       bg="#34495e", fg="#95a5a6")
        self.label_ia_deck.pack(side=tk.LEFT, padx=10)
        
        self.label_ia_mano = tk.Label(info_ia, text="Mano: 5", font=("Arial", 12), 
                                       bg="#34495e", fg="#95a5a6")
        self.label_ia_mano.pack(side=tk.LEFT, padx=10)
        
        # Campo IA
        self.frame_campo_ia = tk.Frame(frame_ia, bg="#34495e")
        self.frame_campo_ia.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame central - Controles y log
        frame_central = tk.Frame(self.root, bg="#2c3e50")
        frame_central.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # Log de eventos
        log_frame = tk.Frame(frame_central, bg="#34495e", relief=tk.SUNKEN, bd=2)
        log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(log_frame, text="📜 Historial de Batalla", font=("Arial", 12, "bold"),
                bg="#34495e", fg="#ecf0f1").pack(pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=50,
                                                  bg="#2c3e50", fg="#ecf0f1",
                                                  font=("Courier", 10))
        self.log_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Controles
        controles_frame = tk.Frame(frame_central, bg="#34495e", relief=tk.RAISED, bd=2)
        controles_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        tk.Label(controles_frame, text="🎮 Controles", font=("Arial", 14, "bold"),
                bg="#34495e", fg="#ecf0f1").pack(pady=10)
        
        self.btn_terminar_turno = tk.Button(controles_frame, text="Terminar Turno",
                                            command=self.terminar_turno,
                                            bg="#27ae60", fg="white",
                                            font=("Arial", 12, "bold"),
                                            width=15, height=2)
        self.btn_terminar_turno.pack(pady=5, padx=10)
        
        self.btn_fusionar = tk.Button(controles_frame, text="Fusionar Cartas",
                                      command=self.iniciar_fusion,
                                      bg="#9b59b6", fg="white",
                                      font=("Arial", 11),
                                      width=15)
        self.btn_fusionar.pack(pady=5, padx=10)
        
        self.btn_atacar = tk.Button(controles_frame, text="Modo Ataque",
                                    command=self.modo_atacar,
                                    bg="#e74c3c", fg="white",
                                    font=("Arial", 11),
                                    width=15)
        self.btn_atacar.pack(pady=5, padx=10)
        
        self.btn_cancelar = tk.Button(controles_frame, text="Cancelar",
                                      command=self.cancelar_accion,
                                      bg="#95a5a6", fg="white",
                                      font=("Arial", 10),
                                      width=15)
        self.btn_cancelar.pack(pady=5, padx=10)
        
        # Indicador de turno
        self.label_turno = tk.Label(controles_frame, text="Tu Turno",
                                    font=("Arial", 12, "bold"),
                                    bg="#3498db", fg="white",
                                    relief=tk.RAISED, bd=3,
                                    width=15, height=2)
        self.label_turno.pack(pady=10, padx=10)
        
        # Frame inferior - Campo del jugador
        frame_jugador = tk.Frame(self.root, bg="#34495e", relief=tk.RAISED, bd=2)
        frame_jugador.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        # Campo jugador
        self.frame_campo_jugador = tk.Frame(frame_jugador, bg="#34495e")
        self.frame_campo_jugador.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Mano del jugador
        mano_container = tk.Frame(frame_jugador, bg="#2c3e50", relief=tk.SUNKEN, bd=2)
        mano_container.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        tk.Label(mano_container, text="🃏 Tu Mano", font=("Arial", 12, "bold"),
                bg="#2c3e50", fg="#ecf0f1").pack(pady=5)
        
        self.frame_mano = tk.Frame(mano_container, bg="#2c3e50")
        self.frame_mano.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Info jugador
        info_jugador = tk.Frame(frame_jugador, bg="#34495e")
        info_jugador.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        self.label_jugador_nombre = tk.Label(info_jugador, text="Jugador", 
                                              font=("Arial", 16, "bold"),
                                              bg="#34495e", fg="#3498db")
        self.label_jugador_nombre.pack(side=tk.LEFT, padx=10)
        
        self.label_jugador_vida = tk.Label(info_jugador, text="LP: 8000", 
                                            font=("Arial", 14),
                                            bg="#34495e", fg="#ecf0f1")
        self.label_jugador_vida.pack(side=tk.LEFT, padx=10)
        
        self.label_jugador_deck = tk.Label(info_jugador, text="Deck: 15", 
                                            font=("Arial", 12),
                                            bg="#34495e", fg="#95a5a6")
        self.label_jugador_deck.pack(side=tk.LEFT, padx=10)
    
    def cargar_imagen_carta(self, carta, width=100, height=140):
        """Carga y redimensiona la imagen de una carta"""
        key = f"{carta.id}_{width}_{height}"
        
        if key in self.imagenes_cache:
            return self.imagenes_cache[key]
        
        try:
            img_path = carta.imagen_path
            if os.path.exists(img_path):
                img = Image.open(img_path)
                img = img.resize((width, height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.imagenes_cache[key] = photo
                return photo
        except Exception as e:
            print(f"Error cargando imagen: {e}")
        
        # Imagen por defecto
        return self.crear_carta_placeholder(carta, width, height)
    
    def crear_carta_placeholder(self, carta, width, height):
        """Crea una carta placeholder si no hay imagen"""
        img = Image.new('RGB', (width, height), color='#8e44ad')
        photo = ImageTk.PhotoImage(img)
        return photo
    
    def mostrar_carta(self, frame, carta, comando=None, seleccionable=True):
        """Muestra una carta en el frame especificado"""
        carta_frame = tk.Frame(frame, bg="#34495e", relief=tk.RAISED, bd=2)
        carta_frame.pack(side=tk.LEFT, padx=3, pady=3)
        
        # Imagen
        imagen = self.cargar_imagen_carta(carta, 80, 110)
        label_img = tk.Label(carta_frame, image=imagen, bg="#34495e")
        label_img.image = imagen  # Mantener referencia
        label_img.pack()
        
        # Nombre
        tk.Label(carta_frame, text=carta.nombre[:15], font=("Arial", 8),
                bg="#34495e", fg="#ecf0f1", wraplength=80).pack()
        
        # Stats
        stats_text = f"⚔️{carta.atk} 🛡️{carta.defensa}"
        if hasattr(carta, 'posicion') and carta.posicion == "defensa":
            stats_text += " [DEF]"
        
        tk.Label(carta_frame, text=stats_text, font=("Arial", 8, "bold"),
                bg="#34495e", fg="#f39c12").pack()
        
        if seleccionable and comando:
            carta_frame.bind("<Button-1>", lambda e: comando(carta))
            label_img.bind("<Button-1>", lambda e: comando(carta))
            carta_frame.config(cursor="hand2")
    
    def _limpiar_frame(self, frame):
        """Elimina todos los widgets dentro de un frame"""
        for widget in frame.winfo_children():
            widget.destroy()

    def actualizar_interfaz(self):
        """Actualiza toda la interfaz con el estado actual del juego"""
        estado = self.juego.obtener_estado_juego()
        
        self._limpiar_frame(self.frame_mano)
        self._limpiar_frame(self.frame_campo_jugador)
        self._limpiar_frame(self.frame_campo_ia)

        # Actualizar info IA
        self.label_ia_vida.config(text=f"LP: {estado['ia']['vida']}")
        self.label_ia_deck.config(text=f"Deck: {estado['ia']['deck_size']}")
        self.label_ia_mano.config(text=f"Mano: {estado['ia']['mano_size']}")
        
        # Actualizar info jugador
        self.label_jugador_vida.config(text=f"LP: {estado['jugador']['vida']}")
        self.label_jugador_deck.config(text=f"Deck: {estado['jugador']['deck_size']}")
        
        # Actualizar campo IA
        for widget in self.frame_campo_ia.winfo_children():
            widget.destroy()
        
        if estado['ia']['campo']:
            for carta in estado['ia']['campo']:
                self.mostrar_carta(self.frame_campo_ia, carta, 
                                  comando=self.seleccionar_objetivo_ia,
                                  seleccionable=(self.modo_seleccion == "atacar"))
        else:
            tk.Label(self.frame_campo_ia, text="Campo vacío",
                    font=("Arial", 12), bg="#34495e", fg="#95a5a6").pack()
        
        # Actualizar campo jugador
        for widget in self.frame_campo_jugador.winfo_children():
            widget.destroy()
        
        if estado['jugador']['campo']:
            for carta in estado['jugador']['campo']:
                self.mostrar_carta(self.frame_campo_jugador, carta,
                                  comando=self.seleccionar_carta_campo)
        else:
            tk.Label(self.frame_campo_jugador, text="Campo vacío",
                    font=("Arial", 12), bg="#34495e", fg="#95a5a6").pack()
        
        # Actualizar mano
        for widget in self.frame_mano.winfo_children():
            widget.destroy()
        
        for carta in estado['jugador']['mano']:
            self.mostrar_carta(self.frame_mano, carta,
                              comando=self.seleccionar_carta_mano)
        
        # Actualizar log
        self.log_text.delete(1.0, tk.END)
        for linea in estado['historial']:
            self.log_text.insert(tk.END, linea + "\n")
        self.log_text.see(tk.END)
        
        # Actualizar indicador de turno
        es_turno_jugador = estado['turno'] == "Jugador"
        self.label_turno.config(
            text="Tu Turno" if es_turno_jugador else "Turno IA",
            bg="#3498db" if es_turno_jugador else "#e74c3c"
        )
        
        # Verificar ganador
        if estado['ganador']:
            self.mostrar_ganador(estado['ganador'])
    
    def seleccionar_carta_mano(self, carta):
        """Maneja la selección de una carta de la mano"""
        if self.juego.turno_actual != self.juego.jugador_humano:
            messagebox.showwarning("Advertencia", "No es tu turno")
            return
        
        if self.modo_seleccion == "fusionar":
            if not self.carta_fusion_1:
                self.carta_fusion_1 = carta
                messagebox.showinfo("Fusión", f"Primera carta: {carta.nombre}\nSelecciona la segunda carta")
            else:
                # Intentar fusión
                exito, resultado = self.juego.fusionar_cartas(self.carta_fusion_1, carta)
                if exito:
                    messagebox.showinfo("¡Fusión exitosa!", 
                                       f"Obtuviste: {resultado.nombre}\nATK: {resultado.atk} DEF: {resultado.defensa}")
                else:
                    messagebox.showerror("Error", "Estas cartas no pueden fusionarse")
                
                self.cancelar_accion()
                self.actualizar_interfaz()
        else:
            # Jugar carta normalmente
            self.carta_seleccionada = carta
            respuesta = messagebox.askyesno("Invocar carta",
                                           f"¿Invocar {carta.nombre}?\nATK: {carta.atk} DEF: {carta.defensa}")
            if respuesta:
                exito, msg = self.juego.jugar_carta_humano(carta, "ataque")
                if exito:
                    self.actualizar_interfaz()
                else:
                    messagebox.showerror("Error", msg)
    
    def seleccionar_carta_campo(self, carta):
        """Maneja la selección de una carta del campo"""
        if self.modo_seleccion == "atacar":
            self.carta_seleccionada = carta
            # Pequeña confirmación visual en consola o título
            print(f"Atacante seleccionado: {carta.nombre}")
            messagebox.showinfo("Ataque", f"Atacante: {carta.nombre}\n\n¡Ahora haz CLIC en la carta enemiga que quieres destruir!")

    def seleccionar_objetivo_ia(self, carta_objetivo):
        """Maneja el ataque a una carta de la IA"""
        if not self.carta_seleccionada:
            messagebox.showwarning("Advertencia", "Primero selecciona tu carta atacante")
            return
        
        exito, msg = self.juego.atacar_carta_humano(self.carta_seleccionada, carta_objetivo)
        if exito:
            self.cancelar_accion()
            self.actualizar_interfaz()
        else:
            messagebox.showerror("Error", msg)
    
    def modo_atacar(self):
        """Activa el modo de ataque"""
        if not self.juego.jugador_humano.tiene_cartas_campo():
            messagebox.showwarning("Advertencia", "No tienes cartas en el campo")
            return
        
        self.modo_seleccion = "atacar"
        
        # --- AGREGAR ESTA LÍNEA ---
        # Esto redibuja las cartas enemigas, ahora con la propiedad "seleccionable=True"
        self.actualizar_interfaz() 
        # --------------------------
        
        messagebox.showinfo("Modo Ataque", "1. Selecciona TU carta atacante.\n2. Luego selecciona la carta ENEMIGA objetivo.")
    
    def iniciar_fusion(self):
        """Inicia el proceso de fusión"""
        if len(self.juego.jugador_humano.mano) < 2:
            messagebox.showwarning("Advertencia", "Necesitas al menos 2 cartas en la mano")
            return
        
        self.modo_seleccion = "fusionar"
        self.carta_fusion_1 = None
        messagebox.showinfo("Fusión", "Selecciona 2 cartas de tu mano para fusionar")
    
    def cancelar_accion(self):
        """Cancela la acción actual"""
        self.modo_seleccion = None
        self.carta_seleccionada = None
        self.carta_fusion_1 = None
        
        # --- AGREGAR ESTA LÍNEA ---
        # Restaura la interfaz al estado normal
        self.actualizar_interfaz()
        # --------------------------
    
    def terminar_turno(self):
        """Termina el turno del jugador"""
        if self.juego.turno_actual != self.juego.jugador_humano:
            messagebox.showwarning("Advertencia", "No es tu turno")
            return
        
        self.cancelar_accion()
        self.juego.cambiar_turno()
        self.actualizar_interfaz()
    
    def mostrar_ganador(self, ganador):
        """Muestra el mensaje de ganador"""
        mensaje = f"🎉 ¡{ganador} ha ganado la partida!"
        resultado = messagebox.askyesno("Fin del juego", 
                                        mensaje + "\n\n¿Jugar de nuevo?")
        if resultado:
            self.reiniciar_juego()
        else:
            self.root.quit()
    
    def reiniciar_juego(self):
        """Reinicia el juego"""
        self.juego.inicializar_juego()
        self.cancelar_accion()
        self.actualizar_interfaz()