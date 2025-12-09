import json
from modelo.carta import Carta
from modelo.juego import Juego

class Controlador:

    def __init__(self):
        self.cartas = []
        self.juego = None

    
    def cargar_cartas_fusion_desde_json(self, ruta_json="datos/fusiones.json"):
        # Carga las cartas de fusión
        try:
            with open(ruta_json, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            cartas_fusion = []
            
            for carta_data in datos:
                # Extraer información relevante
                id_carta = carta_data.get('id')
                nombre = carta_data.get('name', 'Desconocido')
                atk = carta_data.get('atk', 0)
                defensa = carta_data.get('def', 0)
                nivel = carta_data.get('level', 1)
                atributo = carta_data.get('attribute', 'DARK')
                tipo = carta_data.get('race', 'Warrior')
                
                # Ruta de la imagen
                imagen_path = f"datos/imagenes/{id_carta}.jpg"
                
                # Crear objeto Carta
                from modelo.carta import Carta
                carta = Carta(
                    id=id_carta,
                    nombre=nombre,
                    atk=atk,
                    defensa=defensa,
                    nivel=nivel,
                    atributo=atributo,
                    tipo=tipo,
                    imagen_path=imagen_path
                )
                
                cartas_fusion.append(carta)
            
            print(f" {len(cartas_fusion)} cartas de fusión cargadas exitosamente")
            return cartas_fusion
        
        except FileNotFoundError:
            print(f" Error: No se encontró el archivo {ruta_json}")
            return []
        except json.JSONDecodeError:
            print(f" Error: El archivo JSON está mal formado")
            return []
        except Exception as e:
            print(f" Error inesperado: {e}")
            return []
    
    def cargar_cartas_desde_json(self, ruta_json="datos/normales.json"):
        try:
            with open(ruta_json, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            self.cartas = []
            
            for carta_data in datos:
                # Extraer información relevante
                id_carta = carta_data.get('id')
                nombre = carta_data.get('name', 'Desconocido')
                atk = carta_data.get('atk', 0)
                defensa = carta_data.get('def', 0)
                nivel = carta_data.get('level', 1)
                atributo = carta_data.get('attribute', 'DARK')
                tipo = carta_data.get('race', 'Warrior')
                
                # Ruta de la imagen
                imagen_path = f"datos/imagenes/{id_carta}.jpg"
                
                # Crear objeto Carta
                carta = Carta(
                    id=id_carta,
                    nombre=nombre,
                    atk=atk,
                    defensa=defensa,
                    nivel=nivel,
                    atributo=atributo,
                    tipo=tipo,
                    imagen_path=imagen_path
                )
                
                self.cartas.append(carta)
            
            print(f" {len(self.cartas)} cartas cargadas exitosamente")
            return self.cartas
        
        except FileNotFoundError:
            print(f" Error: No se encontró el archivo {ruta_json}")
            return []
        except json.JSONDecodeError:
            print(f" Error: El archivo JSON está mal formado")
            return []
        except Exception as e:
            print(f" Error inesperado: {e}")
            return []
    
    def inicializar_juego(self, tamanio_deck=20):
        if not self.cartas:
            print(" Advertencia: No hay cartas cargadas. Cargando...")
            self.cargar_cartas_desde_json()
        
        if len(self.cartas) < tamanio_deck * 2:
            print(f" Advertencia: Solo hay {len(self.cartas)} cartas disponibles")
            tamanio_deck = len(self.cartas) // 2
        
        from modelo.juego import Juego
        self.juego = Juego(self.cartas, tamanio_deck)
        
        # Carga cartas de fusión
        cartas_fusion = self.cargar_cartas_fusion_desde_json()
        if cartas_fusion:
            self.juego.cargar_cartas_fusion(cartas_fusion)
            print(f" Cartas de fusión cargadas en el juego")
        else:
            print(f" No se pudieron cargar cartas de fusión")
        
        self.juego.inicializar_juego()
        
        print(f" Juego inicializado con decks de {tamanio_deck} cartas")
        return self.juego
    
    def obtener_estadisticas_cartas(self):
        if not self.cartas:
            return "No hay cartas cargadas"
        
        atributos = {}
        tipos = {}
        
        for carta in self.cartas:
            atributos[carta.atributo] = atributos.get(carta.atributo, 0) + 1
            tipos[carta.tipo] = tipos.get(carta.tipo, 0) + 1
        
        stats = f" Estadísticas de cartas:\n"
        stats += f"Total: {len(self.cartas)}\n\n"
        stats += "Atributos:\n"
        for attr, count in sorted(atributos.items()):
            stats += f"  {attr}: {count}\n"
        stats += "\nTipos:\n"
        for tipo, count in sorted(tipos.items(), key=lambda x: x[1], reverse=True)[:10]:
            stats += f"  {tipo}: {count}\n"
        
        return stats
    
    def obtener_cartas_mas_fuertes(self, cantidad=10):
        if not self.cartas:
            return []
        
        return sorted(self.cartas, key=lambda c: c.atk, reverse=True)[:cantidad]
    
    def buscar_carta_por_nombre(self, nombre):
        nombre_lower = nombre.lower()
        return [c for c in self.cartas if nombre_lower in c.nombre.lower()]