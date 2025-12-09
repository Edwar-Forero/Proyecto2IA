# Informe Básico del Proyecto

## 1. Descripción General

Este proyecto implementa una versión simplificada del juego Yu-Gi-Oh! Forbidden Memories utilizando Python. El propósito es desarrollar un entorno jugable entre un jugador humano y una inteligencia artificial controlada mediante el algoritmo Minimax. El proyecto integra componentes de lógica de juego, representación de cartas, fusiones entre cartas, mecánicas de ataque y defensa, y una interfaz gráfica desarrollada con Tkinter.

El objetivo académico principal es aplicar técnicas de inteligencia artificial en un contexto de toma de decisiones adversarial, donde dos participantes compiten en turnos alternados. A diferencia del juego original, en esta adaptación todas las cartas de ambos jugadores y el orden de aparición del mazo son conocidos desde el inicio, lo cual permite a la IA utilizar información completa del estado del juego.

## 2. Alcance del Proyecto

El proyecto contempla:

- Un conjunto limitado de cartas (hasta 40 propuestas por el enunciado).
- Al menos 15 fusiones definidas entre tarjetas, con sus estadísticas resultantes.
- Un sistema de turnos estructurado donde el jugador humano siempre inicia.
- Un tablero con cinco espacios por jugador, siguiendo el estilo visual del juego original.
- Mecánicas básicas de combate: ataque, defensa y resolución de encuentros.
- Una interfaz gráfica que permite gestionar la partida de forma visual.
- La posibilidad de configurar el tamaño del mazo de cada jugador.

## 3. Inteligencia Artificial empleada

El proyecto integra el algoritmo Minimax como base para la toma de decisiones de la IA. Demostramos una separación clara entre lógica de juego, IA y GUI.

Minimax evalúa posiciones futuras mediante exploración de posibles jugadas. En esta versión, la IA considera decisiones basadas en el estado del tablero, las cartas disponibles y las posibles fusiones.

## 4. Arquitectura del Repositorio

El repositorio contiene varias carpetas organizadas por responsabilidad:

- **controlador/**: Manejo de flujo del juego y coordinación entre modelo y GUI.
- **datos/**: Archivos JSON con las cartas, fusiones y datos normalizados.
- **docs/**: Documentación adicional o notas relacionadas al proyecto.
- **gui/**: Código responsable de la interfaz gráfica.
- **modelo/**: Clases que representan la estructura del juego, como cartas, jugadores, fusiones y lógica de IA.

La separación modular facilita que cada componente evolucione de forma independiente.

## 5. Interfaz Gráfica

La GUI utiliza Tkinter y representa el tablero con cinco espacios por jugador, una sección para la mano y controles para reiniciar la partida o visualizar logs. También permite cambiar el tamaño del mazo y visualizar las cartas mediante imágenes cargadas con Pillow.

## 6. Conclusiones Parciales

El proyecto se encuentra en una etapa funcional con estructura sólida. La IA podría expandirse mediante heurísticas más elaboradas y mejoras en la búsqueda Minimax, pero los cimientos del juego, la representación de datos y la interfaz están adecuadamente establecidas.
