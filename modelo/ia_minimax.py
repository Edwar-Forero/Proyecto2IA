import math

class IAMinimax:
    """Implementa el algoritmo Minimax con poda alfa-beta para Yu-Gi-Oh!"""
    
    def __init__(self, profundidad=2):
        self.profundidad = profundidad
        self.fusionador = None
    
    def evaluar_estado(self, jugador_max, jugador_min):
        # Evalúa el estado actual del juego. Retorna un valor positivo si favorece al maximizador, negativo al minimizador.

        # Diferencia de puntos de vida
        diferencia_vida = jugador_max.puntos_vida - jugador_min.puntos_vida
        
        # Fuerza total en el campo
        fuerza_max = sum(c.obtener_poder() for c in jugador_max.campo)
        fuerza_min = sum(c.obtener_poder() for c in jugador_min.campo)
        diferencia_fuerza = fuerza_max - fuerza_min
        
        # Ventaja de cartas
        diferencia_mano = len(jugador_max.mano) - len(jugador_min.mano)
        diferencia_campo = len(jugador_max.campo) - len(jugador_min.campo)
        
        # Bonificación por cartas en ataque
        cartas_ataque_max = sum(1 for c in jugador_max.campo if c.posicion == "ataque")
        cartas_ataque_min = sum(1 for c in jugador_min.campo if c.posicion == "ataque")
        
        # Cálculo ponderado
        evaluacion = (
            diferencia_vida * 2 +
            diferencia_fuerza * 0.5 +
            diferencia_mano * 100 +
            diferencia_campo * 150 +
            (cartas_ataque_max - cartas_ataque_min) * 50
        )
        
        return evaluacion
    
    def minimax(self, jugador_max, jugador_min, profundidad, alfa, beta, es_maximizador):
        # Algoritmo Minimax con poda alfa-beta
        # Condiciones de parada
        if profundidad == 0 or jugador_max.esta_derrotado() or jugador_min.esta_derrotado():
            return self.evaluar_estado(jugador_max, jugador_min)
        
        jugador_actual = jugador_max if es_maximizador else jugador_min
        oponente = jugador_min if es_maximizador else jugador_max
        
        if es_maximizador:
            max_eval = -math.inf
            acciones = self._generar_acciones(jugador_actual, oponente)
            
            for accion in acciones:
                clon_actual = jugador_actual.clonar()
                clon_oponente = oponente.clonar()
                self._aplicar_accion(clon_actual, clon_oponente, accion)
                
                eval = self.minimax(
                    clon_actual if es_maximizador else clon_oponente,
                    clon_oponente if es_maximizador else clon_actual,
                    profundidad - 1,
                    alfa,
                    beta,
                    False
                )
                
                max_eval = max(max_eval, eval)
                alfa = max(alfa, eval)
                
                if beta <= alfa:
                    break
            
            return max_eval
        
        else:
            min_eval = math.inf
            acciones = self._generar_acciones(jugador_actual, oponente)
            
            for accion in acciones:
                clon_actual = jugador_actual.clonar()
                clon_oponente = oponente.clonar()
                self._aplicar_accion(clon_actual, clon_oponente, accion)
                
                eval = self.minimax(
                    clon_oponente if not es_maximizador else clon_actual,
                    clon_actual if not es_maximizador else clon_oponente,
                    profundidad - 1,
                    alfa,
                    beta,
                    True
                )
                
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                
                if beta <= alfa:
                    break
            
            return min_eval
    
    def _generar_acciones(self, jugador, oponente):
        # Genera acciones posibles con estrategia inteligente
        acciones = []
        
        # 1. INVOCAR - Solo si no ha invocado en este turno
        if jugador.puede_jugar_carta() and jugador.mano:
            # Evaluar las mejores cartas para invocar
            cartas_ordenadas = sorted(jugador.mano, key=lambda c: c.atk, reverse=True)
            
            for carta in cartas_ordenadas[:3]:  # Solo las 3 más fuertes
                # Decidir posición inteligentemente
                if oponente.tiene_cartas_campo():
                    carta_enemiga_fuerte = max(oponente.campo, key=lambda c: c.atk)
                    
                    # Invocar en ataque si somos más fuertes
                    if carta.atk > carta_enemiga_fuerte.atk * 1.2:
                        acciones.append(("jugar", (carta, "ataque")))
                    # Invocar en defensa si somos más débiles pero tenemos buena DEF
                    elif carta.defensa > carta.atk:
                        acciones.append(("jugar", (carta, "defensa")))
                    else:
                        # Por defecto ataque (ser agresivo)
                        acciones.append(("jugar", (carta, "ataque")))
                else:
                    # Sin oponente, invocar en defensa (regla del juego)
                    acciones.append(("jugar", (carta, "defensa")))
        
        # 2. CAMBIAR POSICIÓN - Evaluar cambios estratégicos
        for carta in jugador.campo:
            # De defensa a ataque
            if carta.posicion == "defensa":
                if not oponente.campo:
                    # Sin enemigos, cambiar a ataque
                    acciones.append(("cambiar_posicion", carta))
                elif oponente.campo:
                    # Evaluar si es seguro atacar
                    puede_ganar = False
                    for enemigo in oponente.campo:
                        if enemigo.posicion == "ataque" and carta.atk > enemigo.atk:
                            puede_ganar = True
                        elif enemigo.posicion == "defensa" and carta.atk > enemigo.defensa:
                            puede_ganar = True
                    
                    if puede_ganar:
                        acciones.append(("cambiar_posicion", carta))
            
            # De ataque a defensa
            elif carta.posicion == "ataque":
                if oponente.campo:
                    # Calcular si vale la pena quedarse en ataque
                    puede_destruir_algo = False
                    
                    for enemigo in oponente.campo:
                        if enemigo.posicion == "ataque" and carta.atk > enemigo.atk:
                            puede_destruir_algo = True
                            break
                        elif enemigo.posicion == "defensa" and carta.atk > enemigo.defensa:
                            puede_destruir_algo = True
                            break
                    
                    # Si no puede destruir nada y su DEF es mejor, cambiar
                    if not puede_destruir_algo and carta.defensa > carta.atk:
                        acciones.append(("cambiar_posicion", carta))
        
        # 3. ATACAR - Solo ataques inteligentes
        if jugador.tiene_cartas_campo() and oponente.tiene_cartas_campo():
            for atacante in jugador.campo:
                if atacante.posicion == "ataque":
                    # Buscar objetivos válidos
                    for objetivo in oponente.campo:
                        # Atacar cartas en ataque si podemos ganar
                        if objetivo.posicion == "ataque" and atacante.atk > objetivo.atk:
                            acciones.append(("atacar", (atacante, objetivo)))
                        # Atacar cartas en defensa si podemos destruirlas
                        elif objetivo.posicion == "defensa" and atacante.atk > objetivo.defensa:
                            acciones.append(("atacar", (atacante, objetivo)))
                        # Atacar defensas solo si el daño es mínimo (< 300)
                        elif objetivo.posicion == "defensa" and (objetivo.defensa - atacante.atk) < 300:
                            acciones.append(("atacar", (atacante, objetivo)))
        
        # 4. ATAQUE DIRECTO - Máxima prioridad si no hay defensa
        if jugador.tiene_cartas_campo() and not oponente.tiene_cartas_campo():
            for atacante in jugador.campo:
                if atacante.posicion == "ataque":
                    acciones.append(("ataque_directo", atacante))
        
        # 5. Si no hay acciones, pasar
        if not acciones:
            acciones.append(("pasar", None))
        
        # Limitar a las 8 mejores acciones para eficiencia
        return acciones[:8]
    
    def _aplicar_accion(self, jugador, oponente, accion):
        """Aplica una acción al estado clonado"""
        tipo, datos = accion
        
        if tipo == "jugar":
            carta, posicion = datos
            carta_en_mano = next((c for c in jugador.mano if c.nombre == carta.nombre), None)
            if carta_en_mano:
                jugador.jugar_carta(carta_en_mano, posicion)
        
        elif tipo == "atacar":
            atacante, objetivo = datos
            atacante_en_campo = next((c for c in jugador.campo if c.nombre == atacante.nombre), None)
            objetivo_en_campo = next((c for c in oponente.campo if c.nombre == objetivo.nombre), None)
            
            if atacante_en_campo and objetivo_en_campo:
                self._simular_batalla(atacante_en_campo, objetivo_en_campo, jugador, oponente)
        
        elif tipo == "ataque_directo":
            atacante = datos
            atacante_en_campo = next((c for c in jugador.campo if c.nombre == atacante.nombre), None)
            if atacante_en_campo:
                oponente.recibir_danio(atacante_en_campo.atk)
        
        elif tipo == "cambiar_posicion":
            carta = datos
            carta_en_campo = next((c for c in jugador.campo if c.nombre == carta.nombre), None)
            if carta_en_campo:
                carta_en_campo.cambiar_posicion()
    
    def _simular_batalla(self, atacante, defensor, atacante_jugador, defensor_jugador):
        # Simula batalla para clones según reglas de Forbidden Memories
        if defensor.posicion == "ataque":
            # Batalla ATK vs ATK - Daño al jugador por diferencia
            if atacante.atk > defensor.atk:
                diferencia = atacante.atk - defensor.atk
                defensor_jugador.recibir_danio(diferencia)
                defensor_jugador.remover_carta_campo(defensor)
            elif atacante.atk < defensor.atk:
                diferencia = defensor.atk - atacante.atk
                atacante_jugador.recibir_danio(diferencia)
                atacante_jugador.remover_carta_campo(atacante)
            else:
                # Empate - ambas destruidas, SIN daño
                defensor_jugador.remover_carta_campo(defensor)
                atacante_jugador.remover_carta_campo(atacante)
        else:
            # Batalla ATK vs DEF - Sin daño al defensor
            if atacante.atk > defensor.defensa:
                # Destruye pero SIN daño al jugador defensor
                defensor_jugador.remover_carta_campo(defensor)
            elif atacante.atk < defensor.defensa:
                # Daño de retroceso al atacante
                diferencia = defensor.defensa - atacante.atk
                atacante_jugador.recibir_danio(diferencia)
            # Si son iguales, no pasa nada
    
    def elegir_mejor_jugada(self, ia_jugador, oponente):
        # Elige la mejor jugada usando Minimax con priorización inteligente
        mejor_accion = None
        mejor_valor = -math.inf
        
        acciones = self._generar_acciones(ia_jugador, oponente)
        
        # Priorizar acciones por tipo
        acciones_ataque_directo = [a for a in acciones if a[0] == "ataque_directo"]
        acciones_invocar = [a for a in acciones if a[0] == "jugar"]
        acciones_atacar = [a for a in acciones if a[0] == "atacar"]
        acciones_cambio = [a for a in acciones if a[0] == "cambiar_posicion"]
        acciones_pasar = [a for a in acciones if a[0] == "pasar"]
        
        # Ordenar por prioridad estratégica
        # 1. Ataque directo (gana LP inmediatamente)
        # 2. Invocar (aumenta presencia en campo)
        # 3. Atacar (elimina amenazas)
        # 4. Cambiar posición (ajuste táctico)
        # 5. Pasar (última opción)
        acciones_priorizadas = (acciones_ataque_directo + 
                               acciones_invocar + 
                               acciones_atacar + 
                               acciones_cambio + 
                               acciones_pasar)
        
        for accion in acciones_priorizadas:
            # Clonar estado
            clon_ia = ia_jugador.clonar()
            clon_oponente = oponente.clonar()
            
            # Aplicar acción
            self._aplicar_accion(clon_ia, clon_oponente, accion)
            
            # Evaluar con Minimax (el oponente juega después)
            valor = self.minimax(
                clon_ia,
                clon_oponente,
                self.profundidad - 1,
                -math.inf,
                math.inf,
                False  # El siguiente turno es del oponente (minimizador)
            )
            
            # Bonus por tipo de acción (para desempatar)
            tipo_accion = accion[0]
            if tipo_accion == "ataque_directo":
                valor += 500  # Gran bonus por ataque directo
            elif tipo_accion == "atacar":
                valor += 100  # Bonus moderado por atacar
            elif tipo_accion == "jugar":
                valor += 50   # Bonus pequeño por invocar
            
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_accion = accion
        
        return mejor_accion if mejor_accion else ("pasar", None)