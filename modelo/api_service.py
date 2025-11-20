import requests
import os
import json

class YGOCardDownloader:
    BASE_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
    CACHE_JSON = "datos/cartas.json"
    IMG_DIR = "datos/imagenes/"

    def __init__(self, cantidad=100):
        self.cantidad = cantidad
        self._asegurar_directorios()

    def _asegurar_directorios(self):
        if not os.path.exists("datos"):
            os.makedirs("datos")
        if not os.path.exists(self.IMG_DIR):
            os.makedirs(self.IMG_DIR)

    # Cargar cartas desde cache si existe
    def cargar_desde_cache(self):
        if os.path.exists(self.CACHE_JSON):
            print("Cargando cartas desde cache local...")
            with open(self.CACHE_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    # Llamar a la API para obtener todas las cartas
    def descargar_cartas(self):
        print("Descargando TODAS las cartas desde YGOPRODeck...")

        response = requests.get(self.BASE_URL)
        response.raise_for_status()

        data = response.json().get("data", [])

        print(f"Total cartas recibidas: {len(data)}")
        return data


    # Filtrar 100 cartas 
    def filtrar_cartas_validas(self, data):
        print("Filtrando solo monstruos válidos para el juego...")

        monstruos = []

        for c in data:
            tipo = c.get("type", "")
            
            # Filtramos SOLO monstruos normales o de efecto
            if tipo not in [
                "Normal Monster",
                "Effect Monster",
                "Pendulum Effect Monster",
                "Pendulum Normal Monster",
                "Ritual Monster",
                "Fusion Monster"
            ]:
                continue

            # Validaciones adicionales
            if (
                c.get("atk") is None or 
                c.get("def") is None or     # Evita Link Monsters (no tienen DEF)
                c.get("level") is None or   # Evita Xyz/Synchro
                "card_images" not in c
            ):
                continue

            monstruos.append(c)

        print(f"✔ Monstruos filtrados: {len(monstruos)}")

        
        # Ordena por atributo y raza para evitar cartas repetidas o muy similares
        monstruos.sort(key=lambda x: (x["attribute"], x["race"]))

        # Selecciona solo la cantidad especificada
        seleccionados = monstruos[:self.cantidad]

        print(f"Selección final: {len(seleccionados)} cartas")
        return seleccionados


    # Guardar imágenes localmente
    def descargar_imagenes(self, cartas):
        print("Descargando imágenes...")

        for c in cartas:
            id = c["id"]
            img_url = c["card_images"][0]["image_url"]
            img_path = f"{self.IMG_DIR}/{id}.jpg"

            if not os.path.exists(img_path):
                img = requests.get(img_url)
                with open(img_path, "wb") as f:
                    f.write(img.content)

        print("Imágenes guardadas en datos/imagenes/")

    #Guardar JSON final
    def guardar_cache(self, cartas):
        with open(self.CACHE_JSON, "w", encoding="utf-8") as f:
            json.dump(cartas, f, ensure_ascii=False, indent=4)

        print(f"Cartas guardadas en {self.CACHE_JSON}")


    # Método principal para obtener cartas       
    def obtener_cartas(self):
        cache = self.cargar_desde_cache()
        if cache is not None:
            return cache

        data = self.descargar_cartas()
        filtradas = self.filtrar_cartas_validas(data)
        self.descargar_imagenes(filtradas)
        self.guardar_cache(filtradas)
        return filtradas
