import math

class IAMinimax:
    """Implementa el algoritmo Minimax con poda alfa-beta para Yu-Gi-Oh!"""
    
    def __init__(self, profundidad=2):
        self.profundidad = profundidad
        self.fusionador = None
    
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
        """Algoritmo Minimax con poda alfa-beta"""
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
        """Genera acciones posibles limitadas para eficiencia"""
        acciones = []
        
        # 1. Jugar carta más fuerte
        if jugador.puede_jugar_carta() and jugador.mano:
            carta_fuerte = max(jugador.mano, key=lambda c: c.atk)
            
            if oponente.tiene_cartas_campo():
                carta_enemiga = max(oponente.campo, key=lambda c: c.atk)
                posicion = "ataque" if carta_fuerte.atk > carta_enemiga.atk else "defensa"
            else:
                posicion = "defensa"
            
            acciones.append(("jugar", (carta_fuerte, posicion)))
        
        # 2. Atacar (limitado a mejores opciones)
        if jugador.tiene_cartas_campo() and oponente.tiene_cartas_campo():
            for atacante in jugador.campo:
                if atacante.posicion == "ataque":
                    # Solo atacar al objetivo más débil
                    objetivo_debil = min(oponente.campo, key=lambda c: c.obtener_poder())
                    acciones.append(("atacar", (atacante, objetivo_debil)))
                    break  # Solo una opción de ataque para eficiencia
        
        # 3. Ataque directo
        if jugador.tiene_cartas_campo() and not oponente.tiene_cartas_campo():
            for atacante in jugador.campo:
                if atacante.posicion == "ataque":
                    acciones.append(("ataque_directo", atacante))
                    break
        
        # 4. Cambiar posición (solo las más estratégicas)
        for carta in jugador.campo[:2]:  # Solo primeras 2 cartas
            if carta.posicion == "defensa" and not oponente.campo:
                acciones.append(("cambiar_posicion", carta))
            elif carta.posicion == "ataque" and oponente.campo:
                if carta.atk < max(c.atk for c in oponente.campo):
                    acciones.append(("cambiar_posicion", carta))
        
        if not acciones:
            acciones.append(("pasar", None))
        
        return acciones[:5]  # Limitar a 5 acciones máximo
    
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
        """Simula batalla para clones según reglas de Forbidden Memories"""
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
        """Elige la mejor jugada usando Minimax - SIMPLIFICADO"""
        mejor_accion = None
        mejor_valor = -math.inf
        
        acciones = self._generar_acciones(ia_jugador, oponente)
        
        # Priorizar: invocar > atacar > cambiar posición
        acciones_invocar = [a for a in acciones if a[0] == "jugar"]
        acciones_ataque = [a for a in acciones if a[0] in ["atacar", "ataque_directo"]]
        acciones_cambio = [a for a in acciones if a[0] == "cambiar_posicion"]
        acciones_pasar = [a for a in acciones if a[0] == "pasar"]
        
        acciones_priorizadas = acciones_invocar + acciones_ataque + acciones_cambio + acciones_pasar
        
        for accion in acciones_priorizadas:
            clon_ia = ia_jugador.clonar()
            clon_oponente = oponente.clonar()
            self._aplicar_accion(clon_ia, clon_oponente, accion)
            
            valor = self.minimax(
                clon_ia,
                clon_oponente,
                self.profundidad - 1,
                -math.inf,
                math.inf,
                False
            )
            
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_accion = accion
        
        return mejor_accion if mejor_accion else ("pasar", None)