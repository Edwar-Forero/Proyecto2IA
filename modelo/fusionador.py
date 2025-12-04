class Fusionador:
    """Maneja las fusiones de cartas según las reglas de Forbidden Memories"""
    
    def __init__(self):
        # Diccionario de fusiones: (id1, id2) -> resultado
        self.fusiones = {}
        self._inicializar_fusiones()
    
    def _inicializar_fusiones(self):
        """
        Define las fusiones disponibles.
        Formato: (carta1_nombre, carta2_nombre): resultado_nombre
        """
        # Fusiones básicas de ejemplo (puedes agregar más)
        self.fusiones_nombres = {
            # Fusiones DARK
            ("Dark Magician", "Mystical Elf"): "Dark Sage",
            ("Summoned Skull", "Red-Eyes B. Dragon"): "Black Skull Dragon",
            ("Gaia The Fierce Knight", "Curse of Dragon"): "Gaia The Dragon Champion",
            
            # Fusiones LIGHT
            ("Blue-Eyes White Dragon", "Blue-Eyes White Dragon"): "Blue-Eyes Ultimate Dragon",
            ("Mystical Elf", "Celtic Guardian"): "Master & Expert",
            
            # Fusiones WATER
            ("Feral Imp", "Winged Dragon, Guardian of the Fortress #1"): "Fiend Kraken",
            ("Starfish", "Silver Fang"): "Sea King Dragon",
            
            # Fusiones FIRE
            ("Flame Swordsman", "Petit Dragon"): "Flame Champion",
            ("Fireyarou", "Darkfire Soldier #1"): "Twin-Headed Thunder Dragon",
            
            # Fusiones EARTH
            ("Rock Ogre Grotto #1", "Mountain Warrior"): "Minomushi Warrior",
            ("Armored Lizard", "Grass Clown"): "Flower Wolf",
            
            # Fusiones WIND
            ("Silver Fang", "Curtain of the Dark Ones"): "Dark Gray",
            ("Harpie Lady", "Harpie Lady"): "Harpie Lady Sisters",
            
            # Fusiones por tipo
            ("Dragon", "Warrior"): "Dragon Warrior",
            ("Spellcaster", "Fairy"): "Thousand Knives",
            
            # Fusiones adicionales
            ("Beaver Warrior", "Skull Servant"): "Mystic Horseman",
            ("Dark Elf", "Mammoth Graveyard"): "Zombie Warrior",
            ("Witty Phantom", "Trial of Nightmare"): "Reaper of the Cards",
        }
    
    def puede_fusionar(self, carta1, carta2, cartas_disponibles):
        """
        Verifica si dos cartas pueden fusionarse.
        
        Args:
            carta1: Primera carta
            carta2: Segunda carta
            cartas_disponibles: Lista de cartas disponibles para el resultado
        
        Returns:
            Carta resultante o None si no es posible
        """
        # Intentar fusión por nombre exacto
        clave1 = (carta1.nombre, carta2.nombre)
        clave2 = (carta2.nombre, carta1.nombre)
        
        nombre_resultado = None
        if clave1 in self.fusiones_nombres:
            nombre_resultado = self.fusiones_nombres[clave1]
        elif clave2 in self.fusiones_nombres:
            nombre_resultado = self.fusiones_nombres[clave2]
        
        # Si encontramos una fusión por nombre
        if nombre_resultado:
            for carta in cartas_disponibles:
                if carta.nombre == nombre_resultado:
                    return carta.clonar()
        
        # Fusión por atributo (si ambas cartas tienen el mismo atributo)
        if carta1.atributo == carta2.atributo:
            return self._fusion_por_atributo(carta1, carta2, cartas_disponibles)
        
        # Fusión por tipo (si ambas cartas tienen el mismo tipo)
        if carta1.tipo == carta2.tipo:
            return self._fusion_por_tipo(carta1, carta2, cartas_disponibles)
        
        return None
    
    def _fusion_por_atributo(self, carta1, carta2, cartas_disponibles):
        """Fusión genérica basada en atributo compartido"""
        atk_promedio = (carta1.atk + carta2.atk) // 2
        
        # Buscar una carta del mismo atributo con stats similares
        candidatos = [
            c for c in cartas_disponibles 
            if c.atributo == carta1.atributo and 
            abs(c.atk - atk_promedio) < 500
        ]
        
        if candidatos:
            # Retornar la más fuerte de los candidatos
            return max(candidatos, key=lambda c: c.atk).clonar()
        
        return None
    
    def _fusion_por_tipo(self, carta1, carta2, cartas_disponibles):
        """Fusión genérica basada en tipo compartido"""
        atk_promedio = (carta1.atk + carta2.atk) // 2
        
        # Buscar una carta del mismo tipo con stats similares
        candidatos = [
            c for c in cartas_disponibles 
            if c.tipo == carta1.tipo and 
            abs(c.atk - atk_promedio) < 500
        ]
        
        if candidatos:
            return max(candidatos, key=lambda c: c.atk).clonar()
        
        return None
    
    def obtener_fusiones_posibles(self, mano, cartas_disponibles):
        """
        Retorna todas las fusiones posibles con las cartas en mano.
        
        Args:
            mano: Lista de cartas en la mano
            cartas_disponibles: Lista de todas las cartas del juego
        
        Returns:
            Lista de tuplas (carta1, carta2, resultado)
        """
        fusiones = []
        
        for i in range(len(mano)):
            for j in range(i + 1, len(mano)):
                resultado = self.puede_fusionar(mano[i], mano[j], cartas_disponibles)
                if resultado:
                    fusiones.append((mano[i], mano[j], resultado))
        
        return fusiones