import pygame
import numpy as np
import random
import time

# Inicializar Pygame
pygame.init()

# Dimensiones de la pantalla
width, height = 600, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Generador de Laberintos con Solución")

# Colores
bg_color = 25, 25, 25
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Dimensiones de la cuadrícula
nxC, nyC = 25, 25

# Dimensiones de las celdas
dimCW = width / nxC
dimCH = height / nyC

# Estado del juego (0 = camino, 1 = pared, 2 = inicio, 3 = final, 4 = camino de solución)
gameState = np.ones((nxC, nyC), dtype=int)

# Bandera para mostrar solución
show_solution = False

def carve_maze(x, y):
    """Generación de laberinto por retroceso recursivo"""
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    random.shuffle(directions)
    
    for dx, dy in directions:
        nx, ny = x + dx*2, y + dy*2
        
        # Verificar límites y si la celda es una pared
        if (0 < nx < nxC-1 and 0 < ny < nyC-1 and gameState[nx, ny] == 1):
            # Abrir camino
            gameState[nx, ny] = 0
            gameState[x + dx, y + dy] = 0
            carve_maze(nx, ny)

def find_path():
    """Encontrar un camino desde el inicio (2) hasta el final (3) usando búsqueda en anchura"""
    global gameState
    
    # Eliminar cualquier camino previo
    gameState = np.where(gameState == 4, 0, gameState)
    
    # Encontrar coordenadas de inicio y fin
    start = tuple(np.argwhere(gameState == 2)[0])
    end = tuple(np.argwhere(gameState == 3)[0])
    
    # Cola para Búsqueda en Anchura
    queue = [start]
    
    # Diccionario para rastrear el camino
    came_from = {start: None}
    
    # Direcciones de movimiento posibles
    directions = [(0,1), (1,0), (0,-1), (-1,0)]
    
    while queue:
        current = queue.pop(0)
        
        # Si se llega al final, reconstruir y marcar el camino
        if current == end:
            while current is not None:
                if gameState[current[0], current[1]] not in [2, 3]:
                    gameState[current[0], current[1]] = 4
                current = came_from[current]
            return True
        
        # Explorar celdas vecinas
        for dx, dy in directions:
            nx, ny = current[0] + dx, current[1] + dy
            
            # Verificar límites y celdas válidas
            if (0 <= nx < nxC and 0 <= ny < nyC and 
                gameState[nx, ny] in [0, 3] and  # Camino o celda final
                (nx, ny) not in came_from):
                
                queue.append((nx, ny))
                came_from[(nx, ny)] = current
    
    return False

def initialize_maze():
    """Inicializar el laberinto"""
    global gameState, show_solution
    # Reiniciar cuadrícula a paredes
    gameState = np.ones((nxC, nyC), dtype=int)
    
    # Reiniciar bandera de solución
    show_solution = False
    
    # Establecer paredes del borde
    gameState[0, :] = 1
    gameState[-1, :] = 1
    gameState[:, 0] = 1
    gameState[:, -1] = 1
    
    # Punto de inicio (abajo a la izquierda)
    start = (1, 1)
    gameState[start[0], start[1]] = 2
    
    # Punto final (arriba a la derecha)
    end = (nxC-2, nyC-2)
    
    # Bloquear las celdas alrededor del punto final y el inicial
    gameState[end[0]-1, end[1]] = 0  # Arriba
    gameState[end[0], end[1]-1] = 0  # Izquierda
    gameState[end[0]-1, end[1]-1] = 0  # Diagonal
    gameState[1, 2] = 0  
    gameState[2, 2] = 0 
    gameState[2, 1] = 0  
    
    # Establecer punto final
    gameState[end[0], end[1]] = 3
    
    # Generar laberinto usando retroceso recursivo
    carve_maze(start[0], start[1])
    
    # Asegurar que inicio y fin permanezcan claros
    gameState[start[0], start[1]] = 2
    gameState[end[0], end[1]] = 3
    
    # Encontrar camino (sin mostrarlo aún)
    find_path()

# Bucle principal del juego
initialize_maze()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Regenerar laberinto al presionar espacio
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            initialize_maze()
        
        # Mostrar solución al presionar Enter
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            show_solution = not show_solution

    # Limpiar pantalla
    screen.fill(bg_color)

    # Dibujar laberinto
    for y in range(nxC):
        for x in range(nyC):
            poly = [
                (x * dimCW, y * dimCH),
                ((x+1) * dimCW, y * dimCH),
                ((x+1) * dimCW, (y+1) * dimCH),
                (x * dimCW, (y+1) * dimCH)
            ]
            
            # Colorear según el tipo de celda
            if gameState[x, y] == 1:
                pygame.draw.polygon(screen, BLACK, poly, 0)  # Pared (Negro)
            elif gameState[x, y] == 2:
                pygame.draw.polygon(screen, GREEN, poly, 0)  # Inicio (Verde)
            elif gameState[x, y] == 3:
                pygame.draw.polygon(screen, RED, poly, 0)  # Final (Rojo)
            elif show_solution and gameState[x, y] == 4:
                pygame.draw.polygon(screen, BLUE, poly, 0)  # Camino de Solución (Azul)
            else:
                pygame.draw.polygon(screen, WHITE, poly, 0)  # Camino despejado (Blanco)

    # Actualizar pantalla
    pygame.display.flip()
    time.sleep(0.1)

# Salir de Pygame
pygame.quit()