class Jugador:
    # Representa un jugador (humano o IA)
    
    def __init__(self, nombre, deck, puntos_vida=8000):
        self.nombre = nombre
        self.deck = deck.copy()  # Baraja completa
        self.mano = []  # Cartas en mano
        self.campo = []  # Cartas en el campo (máximo 5)
        self.cementerio = []  # Cartas destruidas
        self.puntos_vida = puntos_vida
        self.es_ia = False
    
    def robar_carta(self):
        # Roba una carta del deck a la mano
        if len(self.deck) > 0 and len(self.mano) < 5:
            carta = self.deck.pop(0)
            self.mano.append(carta)
            return carta
        return None
    
    def robar_mano_inicial(self, cantidad=5):
        # Roba la mano inicial del juego
        for _ in range(cantidad):
            self.robar_carta()
    
    def jugar_carta(self, carta, posicion="ataque"):
        # Coloca una carta del mano al campo
        if carta in self.mano and len(self.campo) < 5:
            carta.en_campo = True
            carta.posicion = posicion
            self.mano.remove(carta)
            self.campo.append(carta)
            return True
        return False
    
    def remover_carta_campo(self, carta):
        # Remueve una carta del campo y la envía al cementerio
        if carta in self.campo:
            carta.en_campo = False
            self.campo.remove(carta)
            self.cementerio.append(carta)
            return True
        return False
    
    def recibir_danio(self, cantidad):
        # Reduce los puntos de vida del jugador
        self.puntos_vida -= cantidad
        if self.puntos_vida < 0:
            self.puntos_vida = 0
    
    def esta_derrotado(self):
        # Verifica si el jugador ha perdido, Derrota por Life Points
        if self.puntos_vida <= 0:
            return True

        # Derrota por deck vacío + mano vacía + campo vacío
        if len(self.deck) == 0 and len(self.mano) == 0 and len(self.campo) == 0:
            return True

        return False
    
    def tiene_cartas_campo(self):
        # Verifica si tiene cartas en el campo 
        return len(self.campo) > 0
    
    def puede_jugar_carta(self):
        # Verifica si puede jugar más cartas en el campo
        return len(self.campo) < 5 and len(self.mano) > 0
    
    def clonar(self):
        # Crea una copia profunda del jugador para simulaciones
        clon = Jugador(self.nombre, [], self.puntos_vida)
        
        # Clonar deck
        clon.deck = [c.clonar() for c in self.deck]
        
        # Clonar mano
        clon.mano = [c.clonar() for c in self.mano]
        
        # Clonar campo
        clon.campo = [c.clonar() for c in self.campo]
        
        # Clonar cementerio
        clon.cementerio = [c.clonar() for c in self.cementerio]
        
        clon.es_ia = self.es_ia
        
        return clon
    
    def obtener_carta_mas_fuerte(self):
        # Retorna la carta más fuerte del campo
        if not self.campo:
            return None
        return max(self.campo, key=lambda c: c.obtener_poder())
    
    def __repr__(self):
        return f"{self.nombre} - LP: {self.puntos_vida} | Campo: {len(self.campo)} | Mano: {len(self.mano)} | Deck: {len(self.deck)}"