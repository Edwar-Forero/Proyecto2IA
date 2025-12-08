import tkinter as tk
from tkinter import messagebox, simpledialog
from modelo.api_service import YGOCardDownloader
from controlador.controlador import Controlador
from gui.interfaz import InterfazYuGiOh

def main():
    """Función principal del programa"""
    
    print("=" * 60)
    print(" Yu-Gi-Oh! Forbidden Memories - Minimax AI")
    print("=" * 60)
    
    # Inicializar descargador de cartas
    downloader = YGOCardDownloader(cantidad_normales=100, cantidad_fusiones=50)
    
    # Obtener o descargar cartas
    print("\n Verificando base de datos de cartas...")
    cartas_json = downloader.generar_sets()
    print(f" {len(cartas_json)} cartas disponibles en el sistema")
    
    # Inicializar controlador
    print("\n Inicializando controlador del juego...")
    controlador = Controlador()
    
    # Cargar cartas desde JSON
    cartas_cargadas = controlador.cargar_cartas_desde_json()
    
    if not cartas_cargadas:
        print(" Error crítico: No se pudieron cargar las cartas")
        print(" Ejecuta api_service.py para descargar las cartas")
        return
    
    # Mostrar estadísticas
    print("\n" + controlador.obtener_estadisticas_cartas())
    
    # Mostrar cartas más fuertes
    print("\n Top 5 cartas más fuertes:")
    top_cartas = controlador.obtener_cartas_mas_fuertes(5)
    for i, carta in enumerate(top_cartas, 1):
        print(f"  {i}. {carta.nombre} - ATK: {carta.atk}")
    
    # Crear ventana principal
    root = tk.Tk()
    
    # Configurar tamaño de deck
    tamanio_deck = simpledialog.askinteger(
        "Configuración",
        "¿Cuántas cartas por deck? (10-40)",
        initialvalue=20,
        minvalue=10,
        maxvalue=40
    )
    
    if not tamanio_deck:
        tamanio_deck = 20
    
    # Inicializar juego
    print(f"\n Inicializando juego con decks de {tamanio_deck} cartas...")
    juego = controlador.inicializar_juego(tamanio_deck)
    
    # Crear interfaz gráfica
    print(" Cargando interfaz gráfica...")
    app = InterfazYuGiOh(root, juego)
    
    # Mensaje de bienvenida
    messagebox.showinfo(
        "¡Bienvenido!",
        "Yu-Gi-Oh! Forbidden Memories - Minimax AI\n\n"
        " Objetivo: Reduce los LP del oponente a 0\n\n"
        " Reglas:\n"
        "-Máximo 5 cartas en el campo\n"
        "- Puedes fusionar cartas de tu mano\n"
        "- Ataca en posición de ataque\n"
        "- La IA usa Minimax para decidir\n\n"
        "¡Buena suerte, duelista!"
    )
    
    print("\n ¡Interfaz lista! Iniciando duelo...")
    print("=" * 60)
    
    # Iniciar loop de la interfaz
    root.mainloop()
    
    print("\n Gracias por jugar!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Juego interrumpido por el usuario")
    except Exception as e:
        print(f"\n Error fatal: {e}")
        import traceback
        traceback.print_exc()