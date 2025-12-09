# Informe del Código y Estrategias Utilizadas

## 1. Introducción

Este documento describe la organización interna del código del proyecto, así como la estrategia de inteligencia artificial implementada hasta el momento. El repositorio se centra en recrear una versión simplificada del juego Yu-Gi-Oh! Forbidden Memories, incorporando una estructura modular clara que separa la lógica del juego, los datos, la IA y la interfaz gráfica.

## 2. Estructura del Código

La arquitectura del proyecto está dividida en módulos organizados por carpetas, cada uno con una responsabilidad específica.

### 2.1. Carpeta `modelo/`

Contiene las clases fundamentales del juego:

- **carta.py**: Representa las cartas individuales con atributos como ataque, defensa, tipo y nombre.
- **jugador.py**: Maneja la mano, el mazo, las jugadas y las interacciones del jugador.
- **juego.py**: Coordina las reglas de turno, la resolución de combates y el estado general de la partida.
- **fusionador.py**: Aplica las reglas de fusión basadas en la lista cargada desde los archivos JSON.
- **ia_minimax.py**: Implementa la lógica del algoritmo Minimax.

### 2.2. Carpeta `controlador/`

Incluye archivos que gestionan el flujo del juego y conectan la lógica del modelo con la presentación en la interfaz gráfica.

### 2.3. Carpeta `datos/`

Contiene archivos JSON con la información de cartas, fusiones y normalizaciones necesarias para construir el mazo y las combinaciones disponibles.

### 2.4. Carpeta `gui/`

Aloja la interfaz gráfica (Tkinter). El archivo principal en esta sección es **interfaz.py**, que:

- Muestra el tablero.
- Administra la interacción del usuario.
- Controla los paneles de cartas y las acciones del juego.

## 3. Estrategia de IA Utilizada

La estrategia implementada hasta el momento se basa en el algoritmo **Minimax**. El archivo `ia_minimax.py` establece la estructura necesaria para finalizarlo.

### 3.1. Objetivo de Minimax

Minimax evalúa estados futuros del juego para seleccionar la jugada que maximiza la ventaja del agente (IA) y minimiza la del jugador rival. Este enfoque es habitual en juegos deterministas por turnos.

### 3.2. Componentes Clave ya establecidos

- **Generación de estados futuros**: El código prepara las bases para simular jugadas potenciales.
- **Evaluación del estado**: Se incluye una función preliminar que evalúa estados según atributos del tablero y cartas.
- **Profundidad de búsqueda**: Se estructura la recursión del algoritmo.
