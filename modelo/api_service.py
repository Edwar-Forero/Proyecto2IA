import requests
import os
import json

class YGOCardDownloader:
    BASE_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php"

    CACHE_NORMALES = "datos/normales.json"
    CACHE_FUSIONES = "datos/fusiones.json"

    IMG_DIR = "datos/imagenes/"

    NORMAL_TYPES = [
        "Normal Monster",
        "Effect Monster",
        "Pendulum Effect Monster",
        "Pendulum Normal Monster",
        "Ritual Monster"
    ]

    FUSION_TYPES = ["Fusion Monster"]

    def __init__(self, cantidad_normales=80, cantidad_fusiones=30):
        self.cantidad_normales = cantidad_normales
        self.cantidad_fusiones = cantidad_fusiones
        self._asegurar_directorios()

    # DIRECTORIOS
    def _asegurar_directorios(self):
        if not os.path.exists("datos"):
            os.makedirs("datos")
        if not os.path.exists(self.IMG_DIR):
            os.makedirs(self.IMG_DIR)

    # DESCARGA COMPLETA DE API
    def descargar_cartas(self):
        print("Descargando cartas desde la API YGOPRODeck...")

        response = requests.get(self.BASE_URL)
        response.raise_for_status()

        data = response.json().get("data", [])
        print(f"Total de cartas recibidas: {len(data)}")

        return data

    # FILTRO DE CARTAS NORMALES
    def filtrar_normales(self, data):
        normales = []

        for c in data:
            tipo = c.get("type", "")

            # Solo monstruos NO FUSIÓN
            if tipo not in self.NORMAL_TYPES:
                continue

            # Validaciones extra
            if (
                c.get("atk") is None or
                c.get("def") is None or
                c.get("level") is None or
                "card_images" not in c
            ):
                continue

            normales.append(c)

        print(f"Normales encontradas: {len(normales)}")

        normales.sort(key=lambda x: (x["attribute"], x["race"]))

        return normales[:self.cantidad_normales]

    # FILTRO DE CARTAS DE FUSIÓN
    def filtrar_fusiones(self, data):
        fusiones = []

        for c in data:
            tipo = c.get("type", "")

            if tipo not in self.FUSION_TYPES:
                continue

            # Validaciones extra
            if (
                c.get("atk") is None or
                c.get("def") is None or
                c.get("level") is None or
                "card_images" not in c
            ):
                continue

            fusiones.append(c)

        print(f"Fusiones encontradas: {len(fusiones)}")

        fusiones.sort(key=lambda x: (x["attribute"], x["race"]))

        return fusiones[:self.cantidad_fusiones]

    # DESCARGAR IMÁGENES LOCALMENTE
    def descargar_imagenes(self, cartas):
        print("Descargando imágenes...")

        for c in cartas:
            card_id = c["id"]
            img_url = c["card_images"][0]["image_url"]
            img_path = f"{self.IMG_DIR}/{card_id}.jpg"

            if not os.path.exists(img_path):
                try:
                    img = requests.get(img_url)
                    with open(img_path, "wb") as f:
                        f.write(img.content)
                except Exception as e:
                    print(f"ERROR descargando imagen {card_id}: {e}")

        print("Imágenes guardadas.")

    # GUARDAR JSON
    def guardar_json(self, normales, fusiones):
        with open(self.CACHE_NORMALES, "w", encoding="utf-8") as f:
            json.dump(normales, f, ensure_ascii=False, indent=4)

        with open(self.CACHE_FUSIONES, "w", encoding="utf-8") as f:
            json.dump(fusiones, f, ensure_ascii=False, indent=4)

        print("normales.json y fusiones.json guardados correctamente.")

    # MÉTODO PRINCIPAL
    def generar_sets(self):
        print("Generando sets de cartas...")

        data = self.descargar_cartas()

        normales = self.filtrar_normales(data)
        fusiones = self.filtrar_fusiones(data)

        # Descargar imágenes
        self.descargar_imagenes(normales)
        self.descargar_imagenes(fusiones)

        # Guardar doble JSON
        self.guardar_json(normales, fusiones)

        print("Sets generados correctamente.")
        return normales, fusiones

