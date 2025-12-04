class Carta:
    """Representa una carta monstruo de Yu-Gi-Oh!"""
    
    def __init__(self, id, nombre, atk, defensa, nivel, atributo, tipo, imagen_path):
        self.id = id
        self.nombre = nombre
        self.atk = atk
        self.defensa = defensa
        self.nivel = nivel
        self.atributo = atributo  # DARK, LIGHT, WATER, FIRE, EARTH, WIND
        self.tipo = tipo  # Dragon, Warrior, Spellcaster, etc.
        self.imagen_path = imagen_path
        self.en_campo = False
        self.posicion = "ataque"  # "ataque" o "defensa"
    
    def cambiar_posicion(self):
        """Cambia entre posición de ataque y defensa"""
        self.posicion = "defensa" if self.posicion == "ataque" else "ataque"
    
    def obtener_poder(self):
        """Retorna el poder actual según la posición"""
        return self.atk if self.posicion == "ataque" else self.defensa
    
    def __repr__(self):
        return f"{self.nombre} (ATK:{self.atk}/DEF:{self.defensa})"
    
    def clonar(self):
        """Crea una copia profunda de la carta"""
        copia = Carta(
            self.id, self.nombre, self.atk, self.defensa,
            self.nivel, self.atributo, self.tipo, self.imagen_path
        )
        copia.en_campo = self.en_campo
        copia.posicion = self.posicion
        return copia