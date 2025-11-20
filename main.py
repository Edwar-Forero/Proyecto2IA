from modelo.api_service import YGOCardDownloader

if __name__ == "__main__":
    
    app = YGOCardDownloader(cantidad=100)

    # Obtener cartas (usa cache si ya existe)
    cartas = app.obtener_cartas()

    # Mostrar nombres de las cartas descargadas o cargadas desde cache
    for carta in cartas:
        print(carta.get("name"))
