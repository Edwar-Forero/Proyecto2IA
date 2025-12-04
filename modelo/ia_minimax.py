import math

class IAMinimax:
    """Implementa el algoritmo Minimax con poda alfa-beta para Yu-Gi-Oh!"""
    
    def __init__(self, profundidad=3):
        self.profundidad = profundidad
        self.fusionador = None  # Se asignará desde el juego
    
    def evaluar_estado(self, jugador_max, jugador_min):
        """
        Evalúa el estado actual del juego.
        Retorna un valor positivo si favorece al maximizador, negativo al minimizador.
        """
        # Diferencia de puntos de vida
        diferencia_vida = jugador_max.puntos_vida - jugador_min.puntos_vida
        
        # Fuerza total en el campo
        fuerza_max = sum(c.obtener_poder() for c in jugador_max.campo)
        fuerza_min = sum(c.obtener_poder() for c in jugador_min.campo)
        diferencia_fuerza = fuerza_max - fuerza_min
        
        # Ventaja de cartas en mano
        diferencia_mano = len(jugador_max.mano) - len(jugador_min.mano)
        
        # Ventaja de cartas en campo
        diferencia_campo = len(jugador_max.campo) - len(jugador_min.campo)
        
        # Cálculo ponderado
        evaluacion = (
            diferencia_vida * 2 +           # Vida es importante
            diferencia_fuerza * 0.5 +       # Fuerza en campo
            diferencia_mano * 100 +         # Cartas en mano
            diferencia_campo * 150          # Control del campo
        )
        
        return evaluacion
    
    def minimax(self, jugador_max, jugador_min, profundidad, alfa, beta, es_maximizador):
        """
        Algoritmo Minimax con poda alfa-beta.
        
        Args:
            jugador_max: Jugador que maximiza (IA)
            jugador_min: Jugador que minimiza (oponente)
            profundidad: Profundidad actual de búsqueda
            alfa: Mejor valor para el maximizador
            beta: Mejor valor para el minimizador
            es_maximizador: True si es turno del maximizador
        
        Returns:
            Valor de la evaluación del estado
        """
        # Condiciones de parada
        if profundidad == 0 or jugador_max.esta_derrotado() or jugador_min.esta_derrotado():
            return self.evaluar_estado(jugador_max, jugador_min)
        
        jugador_actual = jugador_max if es_maximizador else jugador_min
        oponente = jugador_min if es_maximizador else jugador_max
        
        if es_maximizador:
            max_eval = -math.inf
            
            # Generar todas las acciones posibles
            acciones = self._generar_acciones(jugador_actual, oponente)
            
            for accion in acciones:
                # Clonar estado
                clon_actual = jugador_actual.clonar()
                clon_oponente = oponente.clonar()
                
                # Aplicar acción
                self._aplicar_accion(clon_actual, clon_oponente, accion)
                
                # Recursión
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
                    break  # Poda beta
            
            return max_eval
        
        else:  # Minimizador
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
                    break  # Poda alfa
            
            return min_eval
    
    def _generar_acciones(self, jugador, oponente):
        """
        Genera todas las acciones posibles para el jugador actual.
        
        Returns:
            Lista de tuplas (tipo_accion, datos)
        """
        acciones = []
        
        # 1. Jugar una carta de la mano al campo
        if jugador.puede_jugar_carta():
            for carta in jugador.mano:
                acciones.append(("jugar", carta))
        
        # 2. Atacar con cartas en el campo
        if jugador.tiene_cartas_campo() and oponente.tiene_cartas_campo():
            for atacante in jugador.campo:
                if atacante.posicion == "ataque":
                    for objetivo in oponente.campo:
                        acciones.append(("atacar", (atacante, objetivo)))
        
        # 3. Ataque directo si el oponente no tiene cartas
        if jugador.tiene_cartas_campo() and not oponente.tiene_cartas_campo():
            for atacante in jugador.campo:
                if atacante.posicion == "ataque":
                    acciones.append(("ataque_directo", atacante))
        
        # 4. Cambiar posición de cartas
        for carta in jugador.campo:
            acciones.append(("cambiar_posicion", carta))
        
        # Si no hay acciones, pasar turno
        if not acciones:
            acciones.append(("pasar", None))
        
        return acciones
    
    def _aplicar_accion(self, jugador, oponente, accion):
        """Aplica una acción al estado del juego clonado"""
        tipo, datos = accion
        
        if tipo == "jugar":
            carta = datos
            if carta in jugador.mano:
                jugador.jugar_carta(carta)
        
        elif tipo == "atacar":
            atacante, objetivo = datos
            if atacante in jugador.campo and objetivo in oponente.campo:
                danio = self._calcular_batalla(atacante, objetivo, jugador, oponente)
        
        elif tipo == "ataque_directo":
            atacante = datos
            if atacante in jugador.campo:
                oponente.recibir_danio(atacante.atk)
        
        elif tipo == "cambiar_posicion":
            carta = datos
            if carta in jugador.campo:
                carta.cambiar_posicion()
    
    def _calcular_batalla(self, atacante, defensor, atacante_jugador, defensor_jugador):
        """Calcula el resultado de una batalla entre dos cartas"""
        if defensor.posicion == "ataque":
            # Batalla ATK vs ATK
            if atacante.atk > defensor.atk:
                diferencia = atacante.atk - defensor.atk
                defensor_jugador.recibir_danio(diferencia)
                defensor_jugador.remover_carta_campo(defensor)
            elif atacante.atk < defensor.atk:
                diferencia = defensor.atk - atacante.atk
                atacante_jugador.recibir_danio(diferencia)
                atacante_jugador.remover_carta_campo(atacante)
            else:
                # Empate, ambas destruidas
                defensor_jugador.remover_carta_campo(defensor)
                atacante_jugador.remover_carta_campo(atacante)
        
        else:  # Posición defensa
            # Batalla ATK vs DEF
            if atacante.atk > defensor.defensa:
                defensor_jugador.remover_carta_campo(defensor)
            elif atacante.atk < defensor.defensa:
                diferencia = defensor.defensa - atacante.atk
                atacante_jugador.recibir_danio(diferencia)
    
    def elegir_mejor_jugada(self, ia_jugador, oponente):
        """
        Elige la mejor jugada usando Minimax.
        
        Returns:
            Tupla (tipo_accion, datos) de la mejor acción
        """
        mejor_accion = None
        mejor_valor = -math.inf
        
        acciones = self._generar_acciones(ia_jugador, oponente)
        
        for accion in acciones:
            # Clonar estado
            clon_ia = ia_jugador.clonar()
            clon_oponente = oponente.clonar()
            
            # Aplicar acción
            self._aplicar_accion(clon_ia, clon_oponente, accion)
            
            # Evaluar con Minimax
            valor = self.minimax(
                clon_ia,
                clon_oponente,
                self.profundidad - 1,
                -math.inf,
                math.inf,
                False  # El siguiente turno es del oponente (minimizador)
            )
            
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_accion = accion
        
        return mejor_accion if mejor_accion else ("pasar", None)