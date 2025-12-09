class Fusionador:
    # Maneja las fusiones de cartas según las reglas de Forbidden Memories
    def __init__(self):
        # Diccionario de fusiones
        self.fusiones = {}
        self.cartas_fusion = []  # Cartas violetas disponibles para resultados
        self._inicializar_fusiones()
    
    def _inicializar_fusiones(self):
        # Fusiones específicas por nombre
        self.fusiones_nombres = {
            # Solo algunas fusiones clave
            ("Dark Magician", "Mystical Elf"): "Dark Sage",
            ("Summoned Skull", "Red-Eyes B. Dragon"): "Black Skull Dragon",
            ("Blue-Eyes White Dragon", "Blue-Eyes White Dragon"): "Blue-Eyes Ultimate Dragon",
        }
    
    def cargar_cartas_fusion(self, cartas_fusion):
        # Carga las cartas de fusión disponibles como resultados
        self.cartas_fusion = cartas_fusion
    
    def puede_fusionar(self, carta1, carta2, cartas_disponibles):
        # Intentar fusión por nombre exacto (prioridad más alta)
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
        
        # Intentar fusión por atributo si son iguales
        if carta1.atributo == carta2.atributo:
            resultado = self._fusion_por_atributo(carta1, carta2, cartas_disponibles)
            if resultado:
                return resultado
        
        # Intentar fusión por tipo si son iguales
        if carta1.tipo == carta2.tipo:
            resultado = self._fusion_por_tipo(carta1, carta2, cartas_disponibles)
            if resultado:
                return resultado
        
        # Si no son del mismo atributo ni tipo, intentar fusión genérica
        # Buscar cualquier carta de fusión que tenga stats razonables
        resultado = self._fusion_generica(carta1, carta2, cartas_disponibles)
        if resultado:
            return resultado
        
        return None
    
    def _fusion_por_atributo(self, carta1, carta2, cartas_disponibles):
        # Fusión genérica basada en atributo compartido
        atk_promedio = (carta1.atk + carta2.atk) // 2
        atributo = carta1.atributo
        
        # Buscar una carta de FUSIÓN del mismo atributo con stats similares o mejores
        # AMPLIADO: Rango más flexible (70% - 200%)
        candidatos = [
            c for c in cartas_disponibles 
            if c.atributo == atributo and 
            c.atk >= atk_promedio * 0.7 and  # Al menos 70% del promedio
            c.atk <= atk_promedio * 2.0 and  # Máximo 200% del promedio
            c.nombre not in [carta1.nombre, carta2.nombre]  # No las mismas cartas
        ]
        
        if candidatos:
            # Retornar la más fuerte de los candidatos
            return max(candidatos, key=lambda c: c.atk).clonar()
        
        return None
    
    def _fusion_por_tipo(self, carta1, carta2, cartas_disponibles):
        # Fusión genérica basada en tipo compartido
        atk_promedio = (carta1.atk + carta2.atk) // 2
        tipo = carta1.tipo
        
        # Buscar una carta de FUSIÓN del mismo tipo con stats similares o mejores
        # AMPLIADO: Rango más flexible (70% - 200%)
        candidatos = [
            c for c in cartas_disponibles 
            if c.tipo == tipo and 
            c.atk >= atk_promedio * 0.7 and
            c.atk <= atk_promedio * 2.0 and
            c.nombre not in [carta1.nombre, carta2.nombre]
        ]
        
        if candidatos:
            return max(candidatos, key=lambda c: c.atk).clonar()
        
        return None
    
    def _fusion_generica(self, carta1, carta2, cartas_disponibles):
        # Fusión genérica cuando no comparten atributo ni tipo
        atk_promedio = (carta1.atk + carta2.atk) // 2
        
        # Buscar cualquier carta de fusión con stats razonables
        # Rango muy amplio: 60% - 250%
        candidatos = [
            c for c in cartas_disponibles 
            if c.atk >= atk_promedio * 0.6 and
            c.atk <= atk_promedio * 2.5 and
            c.nombre not in [carta1.nombre, carta2.nombre]
        ]
        
        if candidatos:
            # Preferir cartas más cercanas al promedio
            candidatos_ordenados = sorted(candidatos, key=lambda c: abs(c.atk - atk_promedio))
            return candidatos_ordenados[0].clonar()
        
        return None
    
    def obtener_fusiones_posibles(self, mano, cartas_disponibles):
        fusiones = []
        
        for i in range(len(mano)):
            for j in range(i + 1, len(mano)):
                resultado = self.puede_fusionar(mano[i], mano[j], cartas_disponibles)
                if resultado:
                    fusiones.append((mano[i], mano[j], resultado))
        
        return fusiones
    
    def es_fusion_beneficiosa(self, carta1, carta2, resultado):
        # Verifica si la fusión es beneficiosa comparando stats
        atk_total_original = carta1.atk + carta2.atk
        def_total_original = carta1.defensa + carta2.defensa
        
        # La fusión debe ser MUCHO mejor para ser considerada beneficiosa
        # Debe tener al menos 80% del ATK combinado (más estricto)
        return (resultado.atk >= atk_total_original * 0.8 and
                resultado.atk > carta1.atk and 
                resultado.atk > carta2.atk)