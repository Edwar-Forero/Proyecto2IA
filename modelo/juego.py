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
        self.fase = "inicio"
        self.historial = []
        
        self.fusionador = Fusionador()
        self.ia = IAMinimax(profundidad=2)  # Reducir profundidad para velocidad
        self.ia.fusionador = self.fusionador
        
        self.ganador = None
        
        # Callback para actualizar interfaz
        self.on_actualizar_interfaz = None
    
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
            
            # 2. IA Ejecuta su lógica (Minimax)
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
        """Ejecuta el turno completo de la IA de forma controlada"""
        self.agregar_historial("--- Turno de la IA ---")
        
        # Lista para rastrear qué cartas ya atacaron
        cartas_que_atacaron = []
        
        # FASE 1: INVOCAR (máximo 1 carta)
        if not self.ia_invoco_carta and self.jugador_ia.puede_jugar_carta():
            accion_invocar = self._ia_intentar_invocar()
            if accion_invocar:
                tipo, datos = accion_invocar
                if tipo == "jugar":
                    carta, posicion = datos
                    carta_real = next((c for c in self.jugador_ia.mano if c.nombre == carta.nombre), None)
                    if carta_real:
                        self.jugador_ia.jugar_carta(carta_real, posicion)
                        self.ia_invoco_carta = True
                        self.agregar_historial(f"IA invocó: {carta_real.nombre} en posición {posicion} (ATK: {carta_real.atk}, DEF: {carta_real.defensa})")
                        
                        # Actualizar interfaz después de invocar
                        if self.on_actualizar_interfaz:
                            self.on_actualizar_interfaz()
        
        # FASE 2: CAMBIAR POSICIONES (estratégicamente)
        cambios_realizados = self._ia_cambiar_posiciones()
        if cambios_realizados > 0 and self.on_actualizar_interfaz:
            self.on_actualizar_interfaz()
        
        # FASE 3: ATACAR (con todas las cartas disponibles)
        if self.jugador_ia.tiene_cartas_campo():
            ataques_realizados = self._ia_realizar_ataques(cartas_que_atacaron)
            if ataques_realizados > 0 and self.on_actualizar_interfaz:
                self.on_actualizar_interfaz()
        
        self.agregar_historial("--- Fin del turno de la IA ---")
        self.verificar_ganador()
    
    def _ia_intentar_invocar(self):
        """La IA intenta invocar la mejor carta usando estrategia"""
        if not self.jugador_ia.mano:
            return None
        
        # Obtener carta más fuerte de la mano
        carta_mas_fuerte = max(self.jugador_ia.mano, key=lambda c: c.atk)
        
        # Decidir posición estratégicamente
        posicion = "ataque"  # Por defecto, ser agresivo
        
        if self.jugador_humano.tiene_cartas_campo():
            carta_enemiga_mas_fuerte = max(self.jugador_humano.campo, key=lambda c: c.atk)
            
            # Solo invocar en defensa si:
            # 1. La carta es significativamente más débil que la del enemigo
            # 2. Y su defensa es mejor que su ataque
            if (carta_mas_fuerte.atk < carta_enemiga_mas_fuerte.atk * 0.7 and 
                carta_mas_fuerte.defensa > carta_mas_fuerte.atk):
                posicion = "defensa"
        else:
            # Si el enemigo no tiene cartas, invocar en defensa (regla del juego)
            posicion = "defensa"
        
        return ("jugar", (carta_mas_fuerte, posicion))
    
    def _ia_cambiar_posiciones(self):
        """La IA cambia posiciones de cartas estratégicamente"""
        cambios = 0
        
        # Evaluar situación de LP
        ia_en_peligro = self.jugador_ia.puntos_vida < 4000
        diferencia_lp = self.jugador_ia.puntos_vida - self.jugador_humano.puntos_vida
        
        for carta in self.jugador_ia.campo[:]:
            # Si está en defensa, evaluar si cambiar a ataque
            if carta.posicion == "defensa":
                deberia_atacar = False
                
                if not self.jugador_humano.campo:
                    # Si el enemigo no tiene cartas, SIEMPRE cambiar a ataque
                    deberia_atacar = True
                else:
                    # Si la IA está ganando por mucho (> 3000 LP), ser más agresivo
                    if diferencia_lp > 3000:
                        carta_mas_debil_enemiga = min(self.jugador_humano.campo, key=lambda c: c.obtener_poder())
                        if carta.atk > carta_mas_debil_enemiga.obtener_poder():
                            deberia_atacar = True
                    else:
                        # Ser conservador, solo cambiar si hay ventaja CLARA
                        carta_mas_fuerte_enemiga = max(self.jugador_humano.campo, key=lambda c: c.atk)
                        carta_mas_debil_enemiga = min(self.jugador_humano.campo, key=lambda c: c.obtener_poder())
                        
                        # Solo cambiar a ataque si podemos destruir algo SIN riesgo
                        if carta_mas_debil_enemiga.posicion == "ataque":
                            if carta.atk > carta_mas_debil_enemiga.atk * 1.5:
                                deberia_atacar = True
                        elif carta.atk > carta_mas_debil_enemiga.defensa * 1.3:
                            deberia_atacar = True
                
                if deberia_atacar:
                    carta.cambiar_posicion()
                    self.agregar_historial(f"IA cambió {carta.nombre} a posición ataque")
                    cambios += 1
            
            # Si está en ataque, evaluar si cambiar a defensa
            elif carta.posicion == "ataque":
                if self.jugador_humano.campo:
                    carta_mas_fuerte_enemiga = max(self.jugador_humano.campo, key=lambda c: c.atk)
                    carta_mas_debil_enemiga = min(self.jugador_humano.campo, key=lambda c: c.obtener_poder())
                    
                    # Calcular si esta carta puede atacar con éxito
                    puede_destruir_algo = False
                    
                    for enemigo in self.jugador_humano.campo:
                        if enemigo.posicion == "ataque" and carta.atk > enemigo.atk:
                            puede_destruir_algo = True
                            break
                        elif enemigo.posicion == "defensa" and carta.atk > enemigo.defensa:
                            puede_destruir_algo = True
                            break
                    
                    # Cambiar a defensa si:
                    if not puede_destruir_algo:
                        # 1. No puede destruir nada Y su defensa es mejor
                        if carta.defensa > carta.atk:
                            carta.cambiar_posicion()
                            self.agregar_historial(f"IA cambió {carta.nombre} a posición defensa (sin objetivos)")
                            cambios += 1
                        # 2. O si va a recibir mucho daño (> 500 LP)
                        elif carta_mas_debil_enemiga.posicion == "defensa":
                            danio_potencial = carta_mas_debil_enemiga.defensa - carta.atk
                            if danio_potencial > 500:
                                carta.cambiar_posicion()
                                self.agregar_historial(f"IA cambió {carta.nombre} a posición defensa (evitar daño)")
                                cambios += 1
                    
                    # Si está en peligro (< 4000 LP), ser más defensivo
                    elif ia_en_peligro:
                        if carta.atk < carta_mas_fuerte_enemiga.atk and carta.defensa > carta.atk:
                            carta.cambiar_posicion()
                            self.agregar_historial(f"IA cambió {carta.nombre} a posición defensa (protección)")
                            cambios += 1
        
        return cambios
    
    def _ia_realizar_ataques(self, cartas_que_atacaron):
        """La IA realiza ataques con todas sus cartas en posición de ataque INTELIGENTEMENTE"""
        ataques = 0
        
        # Si el jugador no tiene cartas, ataque directo
        if not self.jugador_humano.tiene_cartas_campo():
            for atacante in self.jugador_ia.campo:
                if atacante.posicion == "ataque" and atacante not in cartas_que_atacaron:
                    danio = atacante.atk
                    self.jugador_humano.recibir_danio(danio)
                    self.agregar_historial(f"¡Ataque directo! {atacante.nombre} te causa {danio} de daño.")
                    cartas_que_atacaron.append(atacante)
                    ataques += 1
                    
                    self.verificar_ganador()
                    if self.ganador:
                        return ataques
        
        # Si el jugador tiene cartas, atacar SOLO si es beneficioso
        else:
            for atacante in self.jugador_ia.campo[:]:
                if atacante.posicion == "ataque" and atacante not in cartas_que_atacaron:
                    # Buscar el mejor objetivo
                    mejor_objetivo = self._ia_elegir_mejor_objetivo_seguro(atacante)
                    
                    if mejor_objetivo:
                        self.realizar_batalla(atacante, mejor_objetivo, self.jugador_ia, self.jugador_humano)
                        cartas_que_atacaron.append(atacante)
                        ataques += 1
                        
                        if self.ganador:
                            return ataques
                    else:
                        # No hay objetivo seguro, NO atacar
                        self.agregar_historial(f"IA decidió no atacar con {atacante.nombre} (muy arriesgado)")
        
        return ataques
    
    def _ia_elegir_mejor_objetivo(self, atacante):
        """Elige el mejor objetivo para atacar con estrategia agresiva"""
        if not self.jugador_humano.campo:
            return None
        
        # Estrategia 1: Destruir cartas que podamos eliminar
        objetivos_destruibles = []
        
        for c in self.jugador_humano.campo:
            if c.posicion == "ataque" and atacante.atk > c.atk:
                objetivos_destruibles.append(c)
            elif c.posicion == "defensa" and atacante.atk > c.defensa:
                objetivos_destruibles.append(c)
        
        if objetivos_destruibles:
            # Atacar la más fuerte de las destruibles (maximizar daño)
            return max(objetivos_destruibles, key=lambda c: c.obtener_poder())
        
        # Estrategia 2: Si no podemos destruir nada, atacar la más débil
        # para minimizar el daño de retroceso
        return min(self.jugador_humano.campo, key=lambda c: c.obtener_poder())
    
    def _ia_elegir_mejor_objetivo_seguro(self, atacante):
        """Elige un objetivo solo si el ataque es BENEFICIOSO para la IA"""
        if not self.jugador_humano.campo:
            return None
        
        # Opción 1: Buscar cartas en DEFENSA que podamos destruir
        objetivos_defensa_destruibles = [
            c for c in self.jugador_humano.campo 
            if c.posicion == "defensa" and atacante.atk > c.defensa
        ]
        
        if objetivos_defensa_destruibles:
            # Prioridad: destruir la más fuerte en defensa
            return max(objetivos_defensa_destruibles, key=lambda c: c.defensa)
        
        # Opción 2: Buscar cartas en ATAQUE que podamos destruir SIN morir
        objetivos_ataque_destruibles = [
            c for c in self.jugador_humano.campo 
            if c.posicion == "ataque" and atacante.atk > c.atk
        ]
        
        if objetivos_ataque_destruibles:
            # Atacar la más fuerte que podamos destruir (maximiza daño al jugador)
            return max(objetivos_ataque_destruibles, key=lambda c: c.atk)
        
        # Opción 3: Evaluar si vale la pena atacar cartas en defensa
        # SOLO si el daño es MÍNIMO (menos de 300 LP) o si es la única opción
        objetivos_defensa = [
            c for c in self.jugador_humano.campo 
            if c.posicion == "defensa"
        ]
        
        if objetivos_defensa:
            # Calcular el daño que recibiríamos
            mejor_opcion = min(objetivos_defensa, key=lambda c: c.defensa)
            danio_potencial = mejor_opcion.defensa - atacante.atk
            
            # SOLO atacar si el daño es menor a 300 LP
            if danio_potencial < 300:
                return mejor_opcion
        
        # Opción 4: Si hay cartas en ATAQUE pero somos más débiles
        # NO ATACAR - retornar None para evitar suicidios
        return None
    
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
        self.agregar_historial(f" {atacante.nombre} ataca a {defensor.nombre}")
        
        if defensor.posicion == "ataque":
            # Batalla ATK vs ATK - Daño al jugador solo por diferencia
            if atacante.atk > defensor.atk:
                diferencia = atacante.atk - defensor.atk
                defensor_jugador.recibir_danio(diferencia)
                defensor_jugador.remover_carta_campo(defensor)
                self.agregar_historial(f"    {defensor.nombre} destruido! {defensor_jugador.nombre} pierde {diferencia} LP")
            
            elif atacante.atk < defensor.atk:
                diferencia = defensor.atk - atacante.atk
                atacante_jugador.recibir_danio(diferencia)
                atacante_jugador.remover_carta_campo(atacante)
                self.agregar_historial(f"    {atacante.nombre} destruido! {atacante_jugador.nombre} pierde {diferencia} LP")
            
            else:
                # Empate - ambas destruidas, SIN daño a jugadores
                atacante_jugador.remover_carta_campo(atacante)
                defensor_jugador.remover_carta_campo(defensor)
                self.agregar_historial(f"    ¡Ambas cartas destruidas! Sin daño a LP")
        
        else:  # Posición defensa
            # Batalla ATK vs DEF - Sin daño al dueño del defensor
            if atacante.atk > defensor.defensa:
                # Carta en defensa destruida, PERO sin daño al jugador defensor
                defensor_jugador.remover_carta_campo(defensor)
                self.agregar_historial(f"    {defensor.nombre} destruido! (Sin daño a LP)")
            
            elif atacante.atk < defensor.defensa:
                # Ataque fallido - daño al atacante
                diferencia = defensor.defensa - atacante.atk
                atacante_jugador.recibir_danio(diferencia)
                self.agregar_historial(f"    Ataque fallido! {atacante_jugador.nombre} pierde {diferencia} LP")
            
            else:
                # Empate - sin destrucción, sin daño
                self.agregar_historial(f"   ○ Sin daño, {defensor.nombre} resiste.")
        
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
                "campo": self.jugador_ia.campo,
                "deck_size": len(self.jugador_ia.deck),
            },
            "turno": self.turno_actual.nombre,
            "fase": self.fase,
            "historial": self.historial[-100:],
            "ganador": self.ganador.nombre if self.ganador else None
        }