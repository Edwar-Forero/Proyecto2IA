import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import simpledialog
from tkinter import scrolledtext
from PIL import Image, ImageTk, ImageOps
import os

class InterfazYuGiOh:
    """
    Interfaz reorganizada tipo tablero Yu-Gi-Oh:
    - Campo central con 5 slots arriba (IA) y 5 abajo (Jugador).
    - Mano con scroll horizontal en la parte inferior.
    - Panel derecho: controles, indicador de turno y log.
    - Permite configurar tamanio_deck y reiniciar.
    - Soporta modo ataque y defensa.
    """

    SLOT_COUNT = 5
    CARD_W = 100
    CARD_H = 140
    MINI_W = 48 
    MINI_H = 68

    def __init__(self, root, juego):
        self.root = root
        self.juego = juego
        self.root.title("Yu-Gi-Oh! - Minimax (Jugador vs IA)")
        self.root.geometry("1200x900")
        self.root.configure(bg="#0b1220")

        # Variables de selección
        self.carta_seleccionada = None
        self.modo_seleccion = None  # "atacar", "cambiar_posicion" or None

        # Cache de imágenes
        self.imagenes_cache = {}

        # conectar callback del juego
        self.juego.on_actualizar_interfaz = self.actualizar_interfaz

        # Crear layout completo
        self._crear_layout()
        
        # Intentar actualizar vista inicial
        try:
            self.actualizar_interfaz()
        except Exception:
            pass

    def _crear_layout(self):
        # Top bar: título + configuración
        topbar = tk.Frame(self.root, bg="#071025", height=48)
        topbar.pack(side=tk.TOP, fill=tk.X)
        topbar.pack_propagate(False)
        tk.Label(topbar, text="Yu-Gi-Oh: Minimax Duel", font=("Helvetica", 16, "bold"),
                 bg="#071025", fg="#f6f6f6").pack(side=tk.LEFT, padx=12)
        tk.Button(topbar, text="Configurar Deck", command=self._abrir_config_deck).pack(side=tk.LEFT, padx=8)
        tk.Button(topbar, text="Reiniciar Juego", command=self._reiniciar_desde_interfaz).pack(side=tk.LEFT, padx=8)

        # Main area: center board / right controls
        main = tk.Frame(self.root, bg="#081426")
        main.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Center panel: Board (IA arriba, jugador abajo)
        center = tk.Frame(main, bg="#0b1220")
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._crear_tablero(center)

        # Right panel: controles y log
        right = tk.Frame(main, bg="#071025", width=340)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(8,0))
        right.pack_propagate(False)
        self._crear_panel_derecho(right)

    def _crear_tablero(self, parent):
        # Campo IA
        campo_ia_frame = tk.Frame(parent, bg="#0b1220")
        campo_ia_frame.pack(side=tk.TOP, fill=tk.X, pady=(6,20))
        # Info IA: LP y deck count
        info_ia = tk.Frame(campo_ia_frame, bg="#071025")
        info_ia.pack(side=tk.TOP, fill=tk.X, padx=12, pady=(2,6))
        self.label_ia_nombre = tk.Label(info_ia, text="IA", bg="#071025", fg="#f35b5b", font=("Helvetica", 12, "bold"))
        self.label_ia_nombre.pack(side=tk.LEFT, padx=(4,8))
        self.label_ia_vida = tk.Label(info_ia, text="LP: 8000", bg="#071025", fg="#f7f7f7", font=("Helvetica", 12))
        self.label_ia_vida.pack(side=tk.LEFT, padx=6)
        self.label_ia_deckcount = tk.Label(info_ia, text="Deck: 0", bg="#071025", fg="#9aa3b2", font=("Helvetica",10))
        self.label_ia_deckcount.pack(side=tk.LEFT, padx=6)

        # Slots IA (5)
        slots_ia = tk.Frame(campo_ia_frame, bg="#0b1220")
        slots_ia.pack(side=tk.TOP, fill=tk.X, padx=20)
        self.slots_ia = []
        for i in range(self.SLOT_COUNT):
            slot = tk.Frame(slots_ia, bg="#09203a", width=self.CARD_W, height=self.CARD_H+30, relief=tk.RIDGE, bd=2)
            slot.pack(side=tk.LEFT, padx=10, pady=6)
            slot.pack_propagate(False)
            lbl = tk.Label(slot, text="Vacío", bg="#09203a", fg="#9aa3b2")
            lbl.pack(expand=True)
            self.slots_ia.append(slot)

        # Central separator
        mid_info = tk.Frame(parent, bg="#071025", height=24)
        mid_info.pack(fill=tk.X, pady=(4,4))
        mid_info.pack_propagate(False)
        self.label_centro = tk.Label(mid_info, text="Batalla", bg="#071025", fg="#f6f6f6", font=("Helvetica", 11, "bold"))
        self.label_centro.pack()

        # Slots Jugador (5)
        campo_player_frame = tk.Frame(parent, bg="#0b1220")
        campo_player_frame.pack(side=tk.TOP, fill=tk.X, pady=(20,6))
        slots_player = tk.Frame(campo_player_frame, bg="#0b1220")
        slots_player.pack(side=tk.TOP, fill=tk.X, padx=20)
        self.slots_player = []
        for i in range(self.SLOT_COUNT):
            slot = tk.Frame(slots_player, bg="#102a3f", width=self.CARD_W, height=self.CARD_H+30, relief=tk.RIDGE, bd=2)
            slot.pack(side=tk.LEFT, padx=10, pady=6)
            slot.pack_propagate(False)
            lbl = tk.Label(slot, text="Vacío", bg="#102a3f", fg="#cfe7ff")
            lbl.pack(expand=True)
            self.slots_player.append(slot)

        # Info jugador
        info_player = tk.Frame(campo_player_frame, bg="#071025")
        info_player.pack(side=tk.TOP, fill=tk.X, padx=12, pady=(6,2))
        self.label_player_nombre = tk.Label(info_player, text="Jugador", bg="#071025", fg="#77d0ff", font=("Helvetica", 12, "bold"))
        self.label_player_nombre.pack(side=tk.LEFT, padx=(4,8))
        self.label_player_vida = tk.Label(info_player, text="LP: 8000", bg="#071025", fg="#f7f7f7", font=("Helvetica", 12))
        self.label_player_vida.pack(side=tk.LEFT, padx=6)
        self.label_player_deckcount = tk.Label(info_player, text="Deck: 0", bg="#071025", fg="#9aa3b2", font=("Helvetica",10))
        self.label_player_deckcount.pack(side=tk.LEFT, padx=6)

        # Mano con canvas horizontal
        mano_container = tk.Frame(parent, bg="#071025", height=170)
        mano_container.pack(side=tk.TOP, fill=tk.X, pady=(10,4))
        mano_container.pack_propagate(False)

        tk.Label(mano_container, text="Tu Mano", bg="#071025", fg="#cfe7ff", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=8, pady=(6,0))

        self.canvas_mano = tk.Canvas(mano_container, bg="#071025", height=120, highlightthickness=0)
        self.hscroll_mano = tk.Scrollbar(mano_container, orient=tk.HORIZONTAL, command=self.canvas_mano.xview)
        self.canvas_mano.configure(xscrollcommand=self.hscroll_mano.set)
        self.canvas_mano.pack(side=tk.TOP, fill=tk.X, expand=True, padx=8)
        self.hscroll_mano.pack(side=tk.TOP, fill=tk.X, padx=8)

        self.frame_mano = tk.Frame(self.canvas_mano, bg="#071025")
        self.canvas_mano.create_window((0,0), window=self.frame_mano, anchor="nw")

        def _on_mano_config(event):
            self.canvas_mano.configure(scrollregion=self.canvas_mano.bbox("all"))
        self.frame_mano.bind("<Configure>", _on_mano_config)

    def _crear_panel_derecho(self, parent):
        # Indicador de turno
        turn_frame = tk.Frame(parent, bg="#071025")
        turn_frame.pack(fill=tk.X, pady=(12,8), padx=12)
        self.label_turno = tk.Label(turn_frame, text="Turno: -", bg="#071025", fg="#fff", font=("Helvetica", 13, "bold"))
        self.label_turno.pack()

        # Label de estado
        self.label_estado = tk.Label(turn_frame, text="", bg="#071025", fg="#ffcc00", font=("Helvetica", 10))
        self.label_estado.pack(pady=(6,0))

        # Controles
        ctrl_frame = tk.Frame(parent, bg="#071025", relief=tk.RIDGE, bd=1)
        ctrl_frame.pack(fill=tk.X, padx=12, pady=(6,12))

        tk.Label(ctrl_frame, text="Controles", bg="#071025", fg="#cfe7ff", font=("Helvetica", 11, "bold")).pack(pady=(6,0))

        self.btn_modo_atacar = tk.Button(ctrl_frame, text="Modo Ataque", command=self.modo_atacar, width=20)
        self.btn_modo_atacar.pack(pady=6)

        self.btn_cambiar_posicion = tk.Button(ctrl_frame, text="Cambiar Posición", command=self.modo_cambiar_posicion, width=20)
        self.btn_cambiar_posicion.pack(pady=6)

        self.btn_cancelar = tk.Button(ctrl_frame, text="Cancelar", command=self.cancelar_accion, width=20, state=tk.DISABLED)
        self.btn_cancelar.pack(pady=6)

        self.btn_terminar_turno = tk.Button(ctrl_frame, text="Terminar Turno", command=self.terminar_turno, width=20, bg="#27ae60", fg="white")
        self.btn_terminar_turno.pack(pady=(8,12))

        # Log de batalla
        tk.Label(parent, text="Historial", bg="#071025", fg="#f6f6f6", font=("Helvetica", 11, "bold")).pack(pady=(2,6))
        log_frame = tk.Frame(parent, bg="#071025", relief=tk.SUNKEN, bd=1)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0,12))
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, bg="#071025", fg="#e6f6f6", font=("Courier",9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

    def cargar_imagen_carta(self, carta, width=None, height=None, thumbnail=False):
        """Carga imagen, cachea y devuelve PhotoImage"""
        if width is None: width = self.CARD_W
        if height is None: height = self.CARD_H
        key = f"{getattr(carta,'id', id(carta))}_{width}_{height}"
        if key in self.imagenes_cache:
            return self.imagenes_cache[key]

        try:
            img_path = getattr(carta, "imagen_path", None)
            if img_path and os.path.exists(img_path):
                img = Image.open(img_path)
                img = ImageOps.contain(img, (width, height))
                photo = ImageTk.PhotoImage(img)
                self.imagenes_cache[key] = photo
                return photo
        except Exception as e:
            print("Error cargando imagen:", e)

        # Placeholder simple
        img = Image.new("RGBA", (width, height), "#2f4f6f")
        photo = ImageTk.PhotoImage(img)
        self.imagenes_cache[key] = photo
        return photo

    def crear_mini_preview(self, carta):
        return self.cargar_imagen_carta(carta, width=self.MINI_W, height=self.MINI_H)

    def _limpiar_frame(self, frame):
        for w in frame.winfo_children():
            w.destroy()

    def actualizar_interfaz(self):
        """Lee el estado del juego y actualiza toda la UI"""
        estado = self.juego.obtener_estado_juego()

        # Actualizar info básica
        es_turno_jugador = estado.get("turno", "") == self.juego.jugador_humano.nombre
        self.label_turno.config(text=("Tu Turno" if es_turno_jugador else "Turno IA"),
                                bg=("#113344" if es_turno_jugador else "#441111"),
                                fg="#ffffff")

        # Actualizar label de estado según el modo
        if self.modo_seleccion == "atacar":
            if self.carta_seleccionada:
                self.label_estado.config(text=f"Selecciona objetivo para {self.carta_seleccionada.nombre}")
            else:
                self.label_estado.config(text="Selecciona tu carta atacante")
        elif self.modo_seleccion == "cambiar_posicion":
            self.label_estado.config(text="Selecciona una carta para cambiar posición")
        else:
            self.label_estado.config(text="")

        # LP y counts
        self.label_ia_vida.config(text=f"LP: {estado['ia']['vida']}")
        self.label_ia_deckcount.config(text=f"Deck: {estado['ia']['deck_size']}")

        self.label_player_vida.config(text=f"LP: {estado['jugador']['vida']}")
        self.label_player_deckcount.config(text=f"Deck: {estado['jugador']['deck_size']}")

        # Actualizar campos: limpiar
        for slot in self.slots_ia:
            for w in slot.winfo_children(): w.destroy()
            tk.Label(slot, text="Vacío", bg=slot.cget("bg"), fg="#9aa3b2").pack(expand=True)
        for slot in self.slots_player:
            for w in slot.winfo_children(): w.destroy()
            tk.Label(slot, text="Vacío", bg=slot.cget("bg"), fg="#9aa3b2").pack(expand=True)

        # Colocar cartas en campo si existen
        campo_ia = estado['ia'].get('campo', [])
        campo_player = estado['jugador'].get('campo', [])

        # Rellenar IA slots (OBJETIVOS)
        for idx, carta in enumerate(campo_ia[:self.SLOT_COUNT]):
            slot = self.slots_ia[idx]
            for w in slot.winfo_children(): w.destroy()
            
            # Resaltar si es objetivo válido
            if self.modo_seleccion == "atacar" and self.carta_seleccionada:
                slot.config(bg="#4a1515", relief=tk.GROOVE, bd=3)
            else:
                slot.config(bg="#09203a", relief=tk.RIDGE, bd=2)
            
            img = self.cargar_imagen_carta(carta, width=90, height=120)
            lbl = tk.Label(slot, image=img, bg=slot.cget("bg"))
            lbl.image = img
            lbl.pack()
            
            # Mostrar nombre y posición
            nombre_texto = carta.nombre[:12]
            posicion_simbolo = "⚔" if carta.posicion == "ataque" else "🛡"
            tk.Label(slot, text=f"{posicion_simbolo} {nombre_texto}", bg=slot.cget("bg"), fg="#f6f6f6", font=("Helvetica",8)).pack()
            tk.Label(slot, text=f"ATK:{carta.atk} DEF:{carta.defensa}", bg=slot.cget("bg"), fg="#f0d8a8", font=("Helvetica",8)).pack()

            # Lógica de selección con propagación a hijos
            if self.modo_seleccion == "atacar" and self.carta_seleccionada:
                def _make_target_handler(c=carta):
                    return lambda e: self.seleccionar_objetivo_ia(c)
                handler = _make_target_handler()
                
                slot.bind("<Button-1>", handler)
                slot.config(cursor="crosshair")
                for child in slot.winfo_children():
                    child.bind("<Button-1>", handler)
                    child.config(cursor="crosshair")
            else:
                slot.unbind("<Button-1>")
                slot.config(cursor="")
                for child in slot.winfo_children():
                    child.unbind("<Button-1>")
                    child.config(cursor="")

        # Rellenar Jugador slots (ATACANTES)
        for idx, carta in enumerate(campo_player[:self.SLOT_COUNT]):
            slot = self.slots_player[idx]
            for w in slot.winfo_children(): w.destroy()
            
            # Resaltar si está seleccionada
            if self.carta_seleccionada and carta.nombre == self.carta_seleccionada.nombre:
                slot.config(bg="#1a4a1a", relief=tk.GROOVE, bd=3)
            elif self.modo_seleccion == "cambiar_posicion":
                slot.config(bg="#3a3a1a", relief=tk.GROOVE, bd=2)
            else:
                slot.config(bg="#102a3f", relief=tk.RIDGE, bd=2)
            
            img = self.cargar_imagen_carta(carta, width=90, height=120)
            lbl = tk.Label(slot, image=img, bg=slot.cget("bg"))
            lbl.image = img
            lbl.pack()
            
            # Mostrar nombre y posición
            nombre_texto = carta.nombre[:12]
            posicion_simbolo = "⚔" if carta.posicion == "ataque" else "🛡"
            tk.Label(slot, text=f"{posicion_simbolo} {nombre_texto}", bg=slot.cget("bg"), fg="#cfe7ff", font=("Helvetica",8)).pack()
            tk.Label(slot, text=f"ATK:{carta.atk} DEF:{carta.defensa}", bg=slot.cget("bg"), fg="#d0f0d0", font=("Helvetica",8)).pack()

            # Permitir seleccionar carta
            if self.modo_seleccion == "atacar" and not self.carta_seleccionada:
                def _make_attacker_handler(c=carta):
                    return lambda e: self.seleccionar_carta_campo(c)
                handler = _make_attacker_handler()

                slot.bind("<Button-1>", handler)
                slot.config(cursor="hand2")
                for child in slot.winfo_children():
                    child.bind("<Button-1>", handler)
                    child.config(cursor="hand2")
            elif self.modo_seleccion == "cambiar_posicion":
                def _make_change_handler(c=carta):
                    return lambda e: self.cambiar_posicion_carta(c)
                handler = _make_change_handler()

                slot.bind("<Button-1>", handler)
                slot.config(cursor="hand2")
                for child in slot.winfo_children():
                    child.bind("<Button-1>", handler)
                    child.config(cursor="hand2")
            else:
                slot.unbind("<Button-1>")
                if self.modo_seleccion != "atacar":
                    slot.config(cursor="")
                for child in slot.winfo_children():
                    child.unbind("<Button-1>")
                    if self.modo_seleccion != "atacar":
                        child.config(cursor="")

        # Mano del jugador
        for w in self.frame_mano.winfo_children(): w.destroy()
        mano = estado['jugador'].get('mano', [])
        for carta in mano:
            cont = tk.Frame(self.frame_mano, bg="#071025", bd=0, padx=6)
            cont.pack(side=tk.LEFT, padx=6, pady=6)
            img = self.cargar_imagen_carta(carta, width=110, height=150)
            lbl = tk.Label(cont, image=img, bg="#071025")
            lbl.image = img
            lbl.pack()
            tk.Label(cont, text=carta.nombre[:18], bg="#071025", fg="#cfe7ff", font=("Helvetica",8)).pack()
            
            def _hand_handler(e, c=carta):
                self.seleccionar_carta_mano(c)
            
            cont.bind("<Button-1>", _hand_handler)
            lbl.bind("<Button-1>", _hand_handler)
            for child in cont.winfo_children():
                 child.bind("<Button-1>", _hand_handler)
            cont.config(cursor="hand2")

        # Log
        self.log_text.delete(1.0, tk.END)
        for linea in estado.get('historial', []):
            self.log_text.insert(tk.END, linea + "\n")
        self.log_text.see("end")

        # actualizar label central si hay ganador
        if estado.get("ganador"):
            self.mostrar_ganador(estado['ganador'])

    def seleccionar_carta_mano(self, carta):
        """Invocar carta del jugador - permite elegir posición"""
        if self.juego.turno_actual != self.juego.jugador_humano:
            messagebox.showwarning("Advertencia", "No es tu turno")
            return

        if self.juego.humano_invoco_carta:
            messagebox.showinfo("Aviso", "Solo puedes invocar una carta por turno")
            return

        # Verificar si la IA tiene cartas
        ia_tiene_cartas = len(self.juego.jugador_ia.campo) > 0
        
        # Diálogo para seleccionar posición
        dialogo = tk.Toplevel(self.root)
        dialogo.title("Invocar Carta")
        # Ajustar geometría para el contenido
        dialogo.geometry("320x250" if ia_tiene_cartas else "320x220") 
        dialogo.configure(bg="#071025")
        dialogo.transient(self.root)
        dialogo.grab_set()
        
        tk.Label(dialogo, text=f"Invocar: {carta.nombre}", bg="#071025", fg="#fff", font=("Helvetica", 12, "bold")).pack(pady=10)
        tk.Label(dialogo, text=f"ATK: {carta.atk}  |  DEF: {carta.defensa}", bg="#071025", fg="#cfe7ff").pack(pady=5)
        
        posicion_elegida = tk.StringVar(value="ataque" if ia_tiene_cartas else "defensa")
        
        btn_frame = tk.Frame(dialogo, bg="#071025")
        btn_frame.pack(pady=10)
        
        # --- LÓGICA DE RESTRICCIÓN DE POSICIÓN ---
        if ia_tiene_cartas:
            # Opción por defecto: Ataque, si hay cartas IA
            tk.Radiobutton(btn_frame, text="⚔ Modo Ataque", variable=posicion_elegida, value="ataque", 
                          bg="#071025", fg="#ff6b6b", selectcolor="#071025", font=("Helvetica", 10)).pack(pady=5, anchor="w")
            tk.Radiobutton(btn_frame, text="🛡 Modo Defensa", variable=posicion_elegida, value="defensa",
                          bg="#071025", fg="#6baaff", selectcolor="#071025", font=("Helvetica", 10)).pack(pady=5, anchor="w")
        else:
            # Opción obligatoria: Defensa, si no hay cartas IA
            # No se usa Radiobutton para "defensa" sino una etiqueta para hacerlo obligatorio.
            tk.Label(dialogo, text="⚠ La IA no tiene cartas en campo\nSolo puedes invocar en Modo Defensa", 
                     bg="#071025", fg="#ffaa00", font=("Helvetica", 9, "bold")).pack(pady=5)
            tk.Label(btn_frame, text="🛡 Modo Defensa (obligatorio)", bg="#071025", fg="#6baaff", 
                     font=("Helvetica", 11, "bold")).pack(pady=5)
            
        # --- Fin LÓGICA DE RESTRICCIÓN DE POSICIÓN ---

        def confirmar():
            dialogo.destroy()
            # La posición es segura ya que se inicializó a "defensa" si ia_tiene_cartas es False
            posicion = posicion_elegida.get() 
            exito, msg = self.juego.jugar_carta_humano(carta, posicion)
            if not exito:
                messagebox.showerror("Error", msg)
            try:
                self.actualizar_interfaz()
            except Exception:
                pass
        
        def cancelar():
            dialogo.destroy()
        
        # Frame para botones de acción final
        action_btn_frame = tk.Frame(dialogo, bg="#071025")
        action_btn_frame.pack(pady=10)
        
        tk.Button(action_btn_frame, text="✓ Confirmar", command=confirmar, bg="#27ae60", fg="white", width=12).pack(side=tk.LEFT, padx=10)
        tk.Button(action_btn_frame, text="✗ Cancelar", command=cancelar, bg="#e74c3c", fg="white", width=12).pack(side=tk.LEFT, padx=10)

    def seleccionar_carta_campo(self, carta):
        """Selecciona carta atacante (modo atacar)"""
        if self.modo_seleccion != "atacar":
            return
        if not carta:
            return
        if carta.posicion != "ataque":
            messagebox.showwarning("Advertencia", "Solo puedes atacar con cartas en posición de ataque")
            return
        self.carta_seleccionada = carta
        try:
            self.actualizar_interfaz()
        except Exception:
            pass

    def seleccionar_objetivo_ia(self, objetivo):
        """Atacar carta del objetivo con la carta seleccionada"""
        if not self.carta_seleccionada:
            messagebox.showwarning("Advertencia", "Primero selecciona tu carta atacante")
            return
        exito, msg = self.juego.atacar_carta_humano(self.carta_seleccionada, objetivo)
        if not exito:
            messagebox.showerror("Error", msg)
        self.cancelar_accion()
        try:
            self.actualizar_interfaz()
        except Exception:
            pass

    def modo_atacar(self):
        """Activa modo atacar"""
        if self.juego.turno_actual != self.juego.jugador_humano:
            messagebox.showwarning("Advertencia", "No es tu turno")
            return
            
        if not self.juego.jugador_humano.tiene_cartas_campo():
            messagebox.showwarning("Advertencia", "No tienes cartas en el campo")
            return
        
        # Verificar si hay cartas en posición de ataque
        cartas_ataque = [c for c in self.juego.jugador_humano.campo if c.posicion == "ataque"]
        if not cartas_ataque:
            messagebox.showwarning("Advertencia", "No tienes cartas en posición de ataque")
            return
        
        self.modo_seleccion = "atacar"
        self.carta_seleccionada = None
        
        self.btn_cancelar.config(state=tk.NORMAL, bg="#e74c3c", fg="white")
        self.btn_modo_atacar.config(state=tk.DISABLED)
        self.btn_cambiar_posicion.config(state=tk.DISABLED)
        
        try:
            self.actualizar_interfaz()
        except Exception:
            pass

    def modo_cambiar_posicion(self):
        """Activa modo cambiar posición"""
        if self.juego.turno_actual != self.juego.jugador_humano:
            messagebox.showwarning("Advertencia", "No es tu turno")
            return
            
        if not self.juego.jugador_humano.tiene_cartas_campo():
            messagebox.showwarning("Advertencia", "No tienes cartas en el campo")
            return
        
        self.modo_seleccion = "cambiar_posicion"
        self.carta_seleccionada = None
        
        self.btn_cancelar.config(state=tk.NORMAL, bg="#e74c3c", fg="white")
        self.btn_modo_atacar.config(state=tk.DISABLED)
        self.btn_cambiar_posicion.config(state=tk.DISABLED)
        
        try:
            self.actualizar_interfaz()
        except Exception:
            pass

    def cambiar_posicion_carta(self, carta):
        """Cambia la posición de una carta en el campo"""
        if not carta:
            return
        
        nueva_posicion = "defensa" if carta.posicion == "ataque" else "ataque"
        carta.cambiar_posicion()
        
        self.juego.agregar_historial(f"Cambiaste {carta.nombre} a posición {nueva_posicion}")
        
        self.cancelar_accion()
        try:
            self.actualizar_interfaz()
        except Exception:
            pass

    def cancelar_accion(self):
        """Cancela cualquier acción en progreso"""
        self.modo_seleccion = None
        self.carta_seleccionada = None
        
        self.btn_cancelar.config(state=tk.DISABLED, bg="#f0f0f0", fg="black")
        self.btn_modo_atacar.config(state=tk.NORMAL)
        self.btn_cambiar_posicion.config(state=tk.NORMAL)
        
        try:
            self.actualizar_interfaz()
        except Exception:
            pass

    def terminar_turno(self):
        """Terminar turno"""
        if self.juego.turno_actual != self.juego.jugador_humano:
            messagebox.showwarning("Advertencia", "No es tu turno")
            return
        
        self.cancelar_accion()
        self.juego.cambiar_turno()
        try:
            self.actualizar_interfaz()
        except Exception:
            pass

    def _abrir_config_deck(self):
        """Pide al usuario el tamaño del deck"""
        current = getattr(self.juego, "tamanio_deck", 20)
        val = simpledialog.askinteger("Config Deck", "Tamaño del deck por jugador (10-40):", initialvalue=current, minvalue=10, maxvalue=40)
        if val:
            self.juego.tamanio_deck = min(max(10, val), 40)
            self._reiniciar_desde_interfaz()

    def _reiniciar_desde_interfaz(self):
        """Reinicia el juego, limpia visuales y fuerza el estado lógico a 0"""
        
        # 1. Cancelar cualquier acción pendiente primero
        self.cancelar_accion() 

        # 2. Resetear variables de control de la interfaz
        self.carta_seleccionada = None
        self.modo_seleccion = None
        self.label_estado.config(text="") 
        
        # 3. LIMPIEZA VISUAL FORZADA DE LOS SLOTS
        # Limpiar slots IA (quita colores rojos y eventos)
        for slot in self.slots_ia:
            slot.config(bg="#09203a", relief=tk.RIDGE, bd=2, cursor="")
            slot.unbind("<Button-1>")
            for child in slot.winfo_children():
                child.destroy()
            # Restaurar label de vacío visualmente
            tk.Label(slot, text="Vacío", bg="#09203a", fg="#9aa3b2").pack(expand=True)
                
        # Limpiar slots Jugador (quita selección y eventos)
        for slot in self.slots_player:
            slot.config(bg="#102a3f", relief=tk.RIDGE, bd=2, cursor="")
            slot.unbind("<Button-1>") 
            for child in slot.winfo_children():
                child.destroy()
            # Restaurar label de vacío visualmente
            tk.Label(slot, text="Vacío", bg="#102a3f", fg="#cfe7ff").pack(expand=True)

        # 4. Reiniciar la lógica interna del juego
        self.juego.inicializar_juego()
        
        # --- CORRECCIÓN CRÍTICA ---
        # Forzamos la bandera de invocación a False.
        # Esto asegura que, aunque reinicies tras haber invocado, 
        # el nuevo juego sepa que aún no has invocado en este nuevo turno 1.
        self.juego.humano_invoco_carta = False 
        # --------------------------
        
        # 5. Volver a pintar la interfaz con el juego limpio
        try:
            self.actualizar_interfaz()
        except Exception as e:
            print(f"Error actualizando interfaz tras reinicio: {e}")

    def mostrar_ganador(self, ganador):
        """Muestra el diálogo de fin de juego"""
        nombre = ganador if isinstance(ganador, str) else getattr(ganador, "nombre", str(ganador))
        
        self.juego.ganador = None
        
        respuesta = messagebox.askyesno("Fin del juego", f" {nombre} ha ganado la partida!\n¿Jugar de nuevo?")
        
        if respuesta:
            self._reiniciar_desde_interfaz()
        else:
            self.root.quit()