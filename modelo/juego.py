import random
from modelo.jugador import Jugador
from modelo.ia_minimax import IAMinimax
from modelo.fusionador import Fusionador

class Juego:
    """Controla la lógica principal del juego de Yu-Gi-Oh!"""
    
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
        self.fase = "inicio"  # inicio, main, batalla, fin
        self.historial = []
        
        self.fusionador = Fusionador()
        self.ia = IAMinimax(profundidad=3)
        self.ia.fusionador = self.fusionador
        
        self.ganador = None
    
    def inicializar_juego(self):
        """Prepara el juego con decks aleatorios"""
        # IMPORTANTE: Resetear el ganador al inicio
        self.ganador = None
        
        # Limpiar historial previo
        self.historial = []
        
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
        
        # Si el jugador presiona terminar turno, iniciamos la secuencia de la IA
        if self.turno_actual == self.jugador_humano:
            
            self.turno_actual = self.jugador_ia
            self.ia_invoco_carta = False  # <--- Resetear flag

            
            # 1. IA Roba carta
            carta = self.jugador_ia.robar_carta()
            if carta:
                self.agregar_historial(f"IA robó una carta.")
            else:
                 self.agregar_historial(f"IA no puede robar (Deck vacío).")
            
            # 2. IA Ejecuta su lógica (Minimax)
            # Esto bloqueará la ventana momentáneamente mientras piensa
            self.ejecutar_turno_ia()
            
            # Verificar si alguien ganó durante el turno de la IA
            if self.ganador:
                return

            # --- VUELTA AL JUGADOR ---
            self.turno_actual = self.jugador_humano
            self.fase = "main"
            self.humano_invoco_carta = False  # <--- Resetear flag

            
            self.agregar_historial("-" * 20)
            self.agregar_historial("--- TU TURNO ---")
            
            # 3. Humano robar carta (Inicio de nuevo turno)
            carta_humano = self.jugador_humano.robar_carta()
            if carta_humano:
                self.agregar_historial(f"Robaste: {carta_humano.nombre}")
            else:
                self.agregar_historial("¡Tu deck está vacío! No puedes robar.")

        # Nota: El bloque 'else' ya no es necesario aquí porque la IA no tiene botón de "Terminar Turno",
        # ella juega todo su turno de corrido dentro del bloque 'if' anterior.
    
    def ejecutar_turno_ia(self):
        """Ejecuta el turno completo de la IA"""
        self.agregar_historial("--- Turno de la IA ---")
        
        acciones_realizadas = 0
        max_acciones = 3 
        
        while acciones_realizadas < max_acciones:
            # ---> AGREGAR ESTO: Permite que la interfaz no se congele totalmente <---
            # (Si importas tkinter dentro de Juego puede dar error circular, 
            #  si no quieres complicarte, omite esta línea, el código funcionará igual)
            # -----------------------------------------------------------------------
            
            # Obtener mejor jugada
            accion = self.ia.elegir_mejor_jugada(self.jugador_ia, self.jugador_humano)
            
            if not accion or accion[0] == "pasar":
                break
            
            # ... (RESTO DE TU CÓDIGO IGUAL A COMO LO TENÍAS) ...
            tipo, datos = accion
            
            if tipo == "jugar":
                # ... tu logica ...
                carta = datos
                carta_real = next((c for c in self.jugador_ia.mano if c.nombre == carta.nombre), None)
                if carta_real:
                    self.jugador_ia.jugar_carta(carta_real, "ataque")
                    self.agregar_historial(f"IA invocó: {carta_real.nombre} (ATK: {carta_real.atk})")
                    acciones_realizadas += 1
            
            elif tipo == "atacar":
                # ... tu logica ...
                atacante, objetivo = datos
                atacante_real = next((c for c in self.jugador_ia.campo if c.nombre == atacante.nombre), None)
                objetivo_real = next((c for c in self.jugador_humano.campo if c.nombre == objetivo.nombre), None)
                
                if atacante_real and objetivo_real:
                    self.realizar_batalla(atacante_real, objetivo_real, self.jugador_ia, self.jugador_humano)
                    acciones_realizadas += 1
            
            elif tipo == "ataque_directo":
                # ... tu logica ...
                atacante = datos
                atacante_real = next((c for c in self.jugador_ia.campo if c.nombre == atacante.nombre), None)
                
                if atacante_real and not self.jugador_humano.tiene_cartas_campo():
                    danio = atacante_real.atk
                    self.jugador_humano.recibir_danio(danio)
                    self.agregar_historial(f"¡Ataque directo! {atacante_real.nombre} te causa {danio} de daño.")
                    acciones_realizadas += 1
            
            elif tipo == "cambiar_posicion":
                # ... tu logica ...
                carta = datos
                carta_real = next((c for c in self.jugador_ia.campo if c.nombre == carta.nombre), None)
                if carta_real:
                    carta_real.cambiar_posicion()
                    self.agregar_historial(f"IA cambió {carta_real.nombre} a posición {carta_real.posicion}")
                    acciones_realizadas += 1
        
        self.agregar_historial("--- Fin del turno de la IA ---")
        self.verificar_ganador()
    
    def jugar_carta_humano(self, carta, posicion="ataque"):
        if self.turno_actual != self.jugador_humano:
            return False, "No es tu turno"
        
        if carta not in self.jugador_humano.mano:
            return False, "Carta no está en tu mano"
        
        if len(self.jugador_humano.campo) >= 5:
            return False, "Campo lleno (máximo 5 cartas)"
        
        exito = self.jugador_humano.jugar_carta(carta, posicion)
        if exito:
            self.humano_invoco_carta = True  # <--- Marcar que invocó
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
        """Ejecuta una batalla entre dos cartas"""
        self.agregar_historial(f" {atacante.nombre} ataca a {defensor.nombre}")
        
        if defensor.posicion == "ataque":
            # Batalla ATK vs ATK
            if atacante.atk > defensor.atk:
                diferencia = atacante.atk - defensor.atk
                defensor_jugador.recibir_danio(diferencia)
                defensor_jugador.remover_carta_campo(defensor)
                self.agregar_historial(f"   {defensor.nombre} destruido! {defensor_jugador.nombre} pierde {diferencia} LP")
            
            elif atacante.atk < defensor.atk:
                diferencia = defensor.atk - atacante.atk
                atacante_jugador.recibir_danio(diferencia)
                atacante_jugador.remover_carta_campo(atacante)
                self.agregar_historial(f"   {atacante.nombre} destruido! {atacante_jugador.nombre} pierde {diferencia} LP")
            
            else:
                # Empate
                atacante_jugador.remover_carta_campo(atacante)
                defensor_jugador.remover_carta_campo(defensor)
                self.agregar_historial(f"   ¡Ambas cartas destruidas!")
        
        else:  # Posición defensa
            # Batalla ATK vs DEF
            if atacante.atk > defensor.defensa:
                defensor_jugador.remover_carta_campo(defensor)
                self.agregar_historial(f"   {defensor.nombre} destruido!")
            
            elif atacante.atk < defensor.defensa:
                diferencia = defensor.defensa - atacante.atk
                atacante_jugador.recibir_danio(diferencia)
                self.agregar_historial(f"   Ataque fallido! {atacante_jugador.nombre} pierde {diferencia} LP")
            
            else:
                self.agregar_historial(f"   Sin daño, {defensor.nombre} resiste.")
        
        self.verificar_ganador()
    
    def fusionar_cartas(self, carta1, carta2):
        """Intenta fusionar dos cartas de la mano del jugador"""
        if self.turno_actual != self.jugador_humano:
            return False, "No es tu turno"
        
        resultado = self.fusionador.puede_fusionar(carta1, carta2, self.cartas_disponibles)
        
        if resultado:
            # Remover cartas usadas
            self.jugador_humano.mano.remove(carta1)
            self.jugador_humano.mano.remove(carta2)
            self.jugador_humano.cementerio.append(carta1)
            self.jugador_humano.cementerio.append(carta2)
            
            # Agregar resultado a la mano
            self.jugador_humano.mano.append(resultado)
            
            self.agregar_historial(f" Fusión exitosa: {carta1.nombre} + {carta2.nombre} = {resultado.nombre}")
            return True, resultado
        
        return False, "Fusión no disponible"
    
    def verificar_ganador(self):
        """Verifica si hay un ganador"""
        if self.jugador_humano.esta_derrotado():
            self.ganador = self.jugador_ia
            self.agregar_historial(" Has sido derrotado. IA gana.")
        
        elif self.jugador_ia.esta_derrotado():
            self.ganador = self.jugador_humano
            self.agregar_historial(" ¡Victoria! Has derrotado a la IA.")
    
    def agregar_historial(self, mensaje):
        """Agrega un mensaje al historial del juego"""
        self.historial.append(mensaje)
        print(mensaje)  # Para debug
    
    def obtener_estado_juego(self):
        """Retorna el estado actual del juego para la GUI"""
        return {
            "jugador": {
                "nombre": self.jugador_humano.nombre,
                "vida": self.jugador_humano.puntos_vida,
                "mano": self.jugador_humano.mano,
                "campo": self.jugador_humano.campo,
                "deck_size": len(self.jugador_humano.deck),
                "cementerio": len(self.jugador_humano.cementerio)
            },
            "ia": {
                "nombre": self.jugador_ia.nombre,
                "vida": self.jugador_ia.puntos_vida,
                "mano_size": len(self.jugador_ia.mano),
                "campo": self.jugador_ia.campo,
                "deck_size": len(self.jugador_ia.deck),
                "cementerio": len(self.jugador_ia.cementerio)
            },
            "turno": self.turno_actual.nombre,
            "fase": self.fase,
            "historial": self.historial[-10:],  # Últimos 10 mensajes
            "ganador": self.ganador.nombre if self.ganador else None
        }