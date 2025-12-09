import random
from modelo.jugador import Jugador
from modelo.ia_minimax import IAMinimax
from modelo.fusionador import Fusionador

class Juego:
    """Controla la lógica principal del juego de Yu-Gi-Oh!"""
    
    # Agregar estas líneas al método __init__ de la clase Juego:

    def __init__(self, cartas_totales, tamanio_deck=20):
        """
        Inicializa el juego.
        
        Args:
            cartas_totales: Lista de todas las cartas disponibles
            tamanio_deck: Número de cartas por deck (máximo 40)
        """
        self.humano_invoco_carta = False
        self.ia_invoco_carta = False

        self.cartas_disponibles = cartas_totales
        self.tamanio_deck = min(tamanio_deck, 40)
        
        self.jugador_humano = None
        self.jugador_ia = None
        self.turno_actual = None
        self.fase = "inicio"
        self.historial = []
        
        # Inicializar fusionador
        self.fusionador = Fusionador()
        
        # IMPORTANTE: Cargar cartas de fusión separadas
        # Estas son las cartas violetas que se usan como resultado
        self.cartas_fusion = []
        
        # Inicializar IA con referencias al fusionador y cartas
        self.ia = IAMinimax(profundidad=2)
        self.ia.fusionador = self.fusionador
        self.ia.cartas_disponibles = self.cartas_fusion  # Usar cartas de fusión
        
        self.ganador = None
        
        # Callback para actualizar interfaz
        self.on_actualizar_interfaz = None
    
    def cargar_cartas_fusion(self, cartas_fusion):
        """
        Carga las cartas de fusión (violetas) disponibles.
        Estas son las cartas que se obtienen como resultado de fusionar.
        """
        self.cartas_fusion = cartas_fusion
        self.fusionador.cargar_cartas_fusion(cartas_fusion)
        if self.ia:
            self.ia.cartas_disponibles = cartas_fusion
    
    def inicializar_juego(self):
        """Prepara el juego con decks aleatorios"""
        self.ganador = None
        self.historial = []
        self.humano_invoco_carta = False
        self.ia_invoco_carta = False
        
        # Crear decks aleatorios
        deck_completo = self.cartas_disponibles.copy()
        random.shuffle(deck_completo)
        
        # Dividir cartas para cada jugador
        deck_humano = [c.clonar() for c in deck_completo[:self.tamanio_deck]]
        deck_ia = [c.clonar() for c in deck_completo[self.tamanio_deck:self.tamanio_deck*2]]
        
        # Crear jugadores
        self.jugador_humano = Jugador("Jugador", deck_humano)
        self.jugador_ia = Jugador("IA", deck_ia)
        self.jugador_ia.es_ia = True
        
        # Robar manos iniciales
        self.jugador_humano.robar_mano_inicial(5)
        self.jugador_ia.robar_mano_inicial(5)
        
        # El jugador humano siempre empieza
        self.turno_actual = self.jugador_humano
        self.fase = "main"
        
        self.agregar_historial("El juego ha comenzado. Es tu turno.")
    
    def cambiar_turno(self):
        """Cambia al siguiente turno manejando el ciclo completo Jugador -> IA -> Jugador"""
        
        if self.turno_actual == self.jugador_humano:
            self.turno_actual = self.jugador_ia
            self.ia_invoco_carta = False
            
            # 1. IA Roba carta
            carta = self.jugador_ia.robar_carta()
            if carta:
                self.agregar_historial(f"IA robó una carta.")
            else:
                self.agregar_historial(f"IA no puede robar (Deck vacío).")
            
            # Actualizar interfaz antes de que la IA piense
            if self.on_actualizar_interfaz:
                self.on_actualizar_interfaz()
            
            # 2. IA Ejecuta su lógica (Minimax) - UNA sola acción por turno
            self.ejecutar_turno_ia()
            
            # Verificar si alguien ganó durante el turno de la IA
            if self.ganador:
                return

            # --- VUELTA AL JUGADOR ---
            self.turno_actual = self.jugador_humano
            self.fase = "main"
            self.humano_invoco_carta = False
            
            self.agregar_historial("-" * 20)
            self.agregar_historial("--- TU TURNO ---")
            
            # 3. Humano robar carta
            carta_humano = self.jugador_humano.robar_carta()
            if carta_humano:
                self.agregar_historial(f"Robaste: {carta_humano.nombre}")
            else:
                self.agregar_historial("¡Tu deck está vacío! No puedes robar.")
    
    def ejecutar_turno_ia(self):
        """Ejecuta el turno completo de la IA usando MINIMAX para decisiones estratégicas"""
        self.agregar_historial("--- Turno de la IA ---")
        
        # Usar Minimax para obtener la mejor acción
        mejor_accion = self.ia.elegir_mejor_jugada(self.jugador_ia, self.jugador_humano)
        
        if mejor_accion:
            tipo, datos = mejor_accion

            # ← AGREGAR ESTE BLOQUE COMPLETO
            if tipo == "fusionar":
                carta1, carta2, resultado = datos
                c1 = next((c for c in self.jugador_ia.mano if c.nombre == carta1.nombre), None)
                c2 = next((c for c in self.jugador_ia.mano if c.nombre == carta2.nombre and c != c1), None)
                
                if c1 and c2:
                    self.jugador_ia.mano.remove(c1)
                    self.jugador_ia.mano.remove(c2)
                    self.jugador_ia.cementerio.append(c1)
                    self.jugador_ia.cementerio.append(c2)
                    self.jugador_ia.mano.append(resultado)
                    
                    self.agregar_historial(f"⚗️ IA fusionó: {c1.nombre} + {c2.nombre} = {resultado.nombre} (ATK: {resultado.atk})")
                    
                    if self.on_actualizar_interfaz:
                        self.on_actualizar_interfaz()
            
            # FASE 1: INVOCAR (si Minimax lo decide)
            if tipo == "jugar":
                if not self.ia_invoco_carta:
                    carta, posicion = datos
                    carta_real = next((c for c in self.jugador_ia.mano if c.nombre == carta.nombre), None)
                    if carta_real:
                        self.jugador_ia.jugar_carta(carta_real, posicion)
                        self.ia_invoco_carta = True
                        self.agregar_historial(f"IA invocó: {carta_real.nombre} en posición {posicion} (ATK: {carta_real.atk}, DEF: {carta_real.defensa})")
                        
                        if self.on_actualizar_interfaz:
                            self.on_actualizar_interfaz()
            
            # FASE 2: ATACAR (si Minimax lo decide)
            elif tipo == "atacar":
                atacante, objetivo = datos
                atacante_real = next((c for c in self.jugador_ia.campo if c.nombre == atacante.nombre), None)
                objetivo_real = next((c for c in self.jugador_humano.campo if c.nombre == objetivo.nombre), None)
                
                if atacante_real and objetivo_real:
                    self.realizar_batalla(atacante_real, objetivo_real, self.jugador_ia, self.jugador_humano)
                    
                    if self.on_actualizar_interfaz:
                        self.on_actualizar_interfaz()
            
            # FASE 3: ATAQUE DIRECTO (si Minimax lo decide)
            elif tipo == "ataque_directo":
                atacante = datos
                atacante_real = next((c for c in self.jugador_ia.campo if c.nombre == atacante.nombre), None)
                
                if atacante_real and not self.jugador_humano.tiene_cartas_campo():
                    danio = atacante_real.atk
                    self.jugador_humano.recibir_danio(danio)
                    self.agregar_historial(f"¡Ataque directo! {atacante_real.nombre} te causa {danio} de daño.")
                    
                    self.verificar_ganador()
                    if self.on_actualizar_interfaz:
                        self.on_actualizar_interfaz()
            
            # FASE 4: CAMBIAR POSICIÓN (si Minimax lo decide)
            elif tipo == "cambiar_posicion":
                carta = datos
                carta_real = next((c for c in self.jugador_ia.campo if c.nombre == carta.nombre), None)
                if carta_real:
                    posicion_anterior = carta_real.posicion
                    carta_real.cambiar_posicion()
                    self.agregar_historial(f"IA cambió {carta_real.nombre} de {posicion_anterior} a {carta_real.posicion}")
                    
                    if self.on_actualizar_interfaz:
                        self.on_actualizar_interfaz()
        
        self.agregar_historial("--- Fin del turno de la IA ---")
        self.verificar_ganador()
    
    def jugar_carta_humano(self, carta, posicion="ataque"):
        """El jugador humano invoca una carta"""
        if self.turno_actual != self.jugador_humano:
            return False, "No es tu turno"
        
        if self.humano_invoco_carta:
            return False, "Solo puedes invocar una carta por turno"
        
        if carta not in self.jugador_humano.mano:
            return False, "Carta no está en tu mano"
        
        if len(self.jugador_humano.campo) >= 5:
            return False, "Campo lleno (máximo 5 cartas)"
        
        exito = self.jugador_humano.jugar_carta(carta, posicion)
        if exito:
            self.humano_invoco_carta = True
            self.agregar_historial(f"Invocaste: {carta.nombre} en posición {posicion}")
            return True, "Carta jugada exitosamente"
        
        return False, "Error al jugar la carta"
    
    def atacar_carta_humano(self, atacante, objetivo):
        """El jugador humano ataca con una carta"""
        if self.turno_actual != self.jugador_humano:
            return False, "No es tu turno"
        
        if atacante not in self.jugador_humano.campo:
            return False, "Carta no está en tu campo"
        
        if atacante.posicion != "ataque":
            return False, "La carta debe estar en posición de ataque"
        
        if objetivo not in self.jugador_ia.campo:
            return False, "Objetivo inválido"
        
        self.realizar_batalla(atacante, objetivo, self.jugador_humano, self.jugador_ia)
        return True, "Ataque realizado"
    
    def ataque_directo_humano(self, atacante):
        """Ataque directo a los puntos de vida del oponente"""
        if not self.jugador_ia.tiene_cartas_campo():
            danio = atacante.atk
            self.jugador_ia.recibir_danio(danio)
            self.agregar_historial(f"¡Ataque directo! {atacante.nombre} causa {danio} de daño.")
            self.verificar_ganador()
            return True, "Ataque directo realizado"
        
        return False, "El oponente tiene cartas en el campo"
    
    def realizar_batalla(self, atacante, defensor, atacante_jugador, defensor_jugador):
        """Ejecuta una batalla entre dos cartas según las reglas de Forbidden Memories"""
        self.agregar_historial(f"⚔ {atacante.nombre} ataca a {defensor.nombre}")
        
        if defensor.posicion == "ataque":
            # Batalla ATK vs ATK - Daño al jugador solo por diferencia
            if atacante.atk > defensor.atk:
                diferencia = atacante.atk - defensor.atk
                defensor_jugador.recibir_danio(diferencia)
                defensor_jugador.remover_carta_campo(defensor)
                self.agregar_historial(f"   - {defensor.nombre} destruido! {defensor_jugador.nombre} pierde {diferencia} LP")
            
            elif atacante.atk < defensor.atk:
                diferencia = defensor.atk - atacante.atk
                atacante_jugador.recibir_danio(diferencia)
                atacante_jugador.remover_carta_campo(atacante)
                self.agregar_historial(f"   - {atacante.nombre} destruido! {atacante_jugador.nombre} pierde {diferencia} LP")
            
            else:
                # Empate - ambas destruidas, SIN daño a jugadores
                atacante_jugador.remover_carta_campo(atacante)
                defensor_jugador.remover_carta_campo(defensor)
                self.agregar_historial(f"   - ¡Ambas cartas destruidas! Sin daño a LP")
        
        else:  # Posición defensa
            # Batalla ATK vs DEF - Sin daño al dueño del defensor
            if atacante.atk > defensor.defensa:
                # Carta en defensa destruida, PERO sin daño al jugador defensor
                defensor_jugador.remover_carta_campo(defensor)
                self.agregar_historial(f"   - {defensor.nombre} destruido! (Sin daño a LP)")
            
            elif atacante.atk < defensor.defensa:
                # Ataque fallido - daño al atacante
                diferencia = defensor.defensa - atacante.atk
                atacante_jugador.recibir_danio(diferencia)
                self.agregar_historial(f"   - Ataque fallido! {atacante_jugador.nombre} pierde {diferencia} LP")
            
            else:
                # Empate - sin destrucción, sin daño
                self.agregar_historial(f"   - Sin daño, {defensor.nombre} resiste.")
        
        self.verificar_ganador()
    
    def fusionar_cartas(self, carta1, carta2):
        """Intenta fusionar dos cartas de la mano del jugador"""
        if self.turno_actual != self.jugador_humano:
            return False, "No es tu turno"
        
        # IMPORTANTE: Usar cartas_fusion (violetas) como disponibles
        cartas_fusion_disponibles = self.cartas_fusion if hasattr(self, 'cartas_fusion') and self.cartas_fusion else []
        
        if not cartas_fusion_disponibles:
            return False, "No hay cartas de fusión disponibles en el sistema"
        
        # Intentar fusionar usando las cartas de fusión
        resultado = self.fusionador.puede_fusionar(carta1, carta2, cartas_fusion_disponibles)
        
        if resultado:
            # Remover cartas usadas de la mano
            self.jugador_humano.mano.remove(carta1)
            self.jugador_humano.mano.remove(carta2)
            self.jugador_humano.cementerio.append(carta1)
            self.jugador_humano.cementerio.append(carta2)
            
            # Agregar resultado a la mano
            self.jugador_humano.mano.append(resultado)
            
            self.agregar_historial(f"Fusión exitosa: {carta1.nombre} + {carta2.nombre} = {resultado.nombre} (ATK: {resultado.atk})")
            return True, resultado
        
        return False, "Fusión no disponible"
    
    # Dentro de la clase Juego

    def verificar_ganador(self):
        """Verifica si hay un ganador"""
        
        # 1. Verificar si el Jugador Humano perdió
        if self.jugador_humano.esta_derrotado():
            self.ganador = self.jugador_ia
            
            # Determinar la causa de la derrota para el historial
            if self.jugador_humano.puntos_vida <= 0:
                self.agregar_historial(" Has sido derrotado. IA gana por Puntos de Vida.")
            else:
                self.agregar_historial(" Has sido derrotado. IA gana por DECK OUT (Deck, Mano y Campo vacíos).")
        
        # 2. Verificar si la IA perdió
        elif self.jugador_ia.esta_derrotado():
            self.ganador = self.jugador_humano
            
            # Determinar la causa de la victoria para el historial
            if self.jugador_ia.puntos_vida <= 0:
                self.agregar_historial(" ¡Victoria! Has derrotado a la IA por Puntos de Vida.")
            else:
                self.agregar_historial(" ¡Victoria! Has derrotado a la IA por DECK OUT (Deck, Mano y Campo vacíos).")
    
    def agregar_historial(self, mensaje):
        """Agrega un mensaje al historial del juego"""
        self.historial.append(mensaje)
        print(mensaje)
    
    def obtener_estado_juego(self):
        """Retorna el estado actual del juego para la GUI"""
        return {
            "jugador": {
                "nombre": self.jugador_humano.nombre,
                "vida": self.jugador_humano.puntos_vida,
                "mano": self.jugador_humano.mano,
                "campo": self.jugador_humano.campo,
                "deck_size": len(self.jugador_humano.deck),
            },
            "ia": {
                "nombre": self.jugador_ia.nombre,
                "vida": self.jugador_ia.puntos_vida,
                "mano_size": len(self.jugador_ia.mano),
                "mano": self.jugador_ia.mano,
                "campo": self.jugador_ia.campo,
                "deck_size": len(self.jugador_ia.deck),
            },
            "turno": self.turno_actual.nombre,
            "fase": self.fase,
            "historial": self.historial[-100:],
            "ganador": self.ganador.nombre if self.ganador else None
        }