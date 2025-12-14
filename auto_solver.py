import pyautogui
import time
import sys
import os
from pathlib import Path
import webbrowser
from typing import Tuple, Optional
import cv2
import numpy as np

# Asegurarse de que el directorio actual esté en el path para importar
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar el detector de Sudoku existente
try:
    from main import SudokuBoardDetector
except ImportError as e:
    print(f"Error al importar SudokuBoardDetector: {e}")
    print("Asegúrate de tener el archivo main.py en el mismo directorio")
    sys.exit(1)

class SudokuAutoSolver:
    """Clase para automatizar la resolución de Sudoku en sudoku.com"""
    
    def __init__(self, browser_url: str = "https://sudoku.com"):
        """
        Inicializa el solucionador automático de Sudoku.
        
        Args:
            browser_url: URL del sitio web de Sudoku (por defecto: sudoku.com)
        """
        self.browser_url = browser_url
        self.detector = SudokuBoardDetector()
        
        # Configuración de pyautogui
        pyautogui.PAUSE = 0.1  # Pausa entre acciones
        pyautogui.FAILSAFE = True  # Habilitar seguridad
        
        # Dimensiones de la pantalla
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Variables para almacenar coordenadas del tablero
        self.board_region = None
        self.cell_positions = None
        
        print("Inicializando Sudoku Auto Solver...")
        print(f"Resolución de pantalla: {self.screen_width}x{self.screen_height}")
    
    def open_browser_and_navigate(self) -> bool:
        """
        Abre el navegador y navega a sudoku.com
        
        Returns:
            True si se abrió correctamente, False en caso contrario
        """
        try:
            print(f"Abriendo navegador en: {self.browser_url}")
            
            # Usar webbrowser para abrir la URL
            webbrowser.open(self.browser_url)
            
            # Esperar a que cargue la página
            print("Esperando a que cargue la página...")
            time.sleep(5)
            
            # Maximizar la ventana (si es necesario)
            pyautogui.hotkey('f11')  # Alternar pantalla completa
            time.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"Error al abrir el navegador: {e}")
            return False
    
    def capture_game_screenshot(self, save_path: str = "sudoku_screenshot.png") -> Optional[np.ndarray]:
        """
        Captura una screenshot del juego y la guarda.
        
        Args:
            save_path: Ruta donde guardar la captura
            
        Returns:
            Imagen capturada o None si falla
        """
        try:
            # Primero, hacer clic en cualquier lugar para enfocar la ventana
            pyautogui.click(x=100, y=100)
            time.sleep(0.5)
            
            print("Tomando captura de pantalla del juego...")
            
            # Tomar screenshot completa
            screenshot = pyautogui.screenshot()
            
            # Convertir a array numpy para OpenCV
            screenshot_np = np.array(screenshot)
            
            # Convertir de RGB a BGR (formato OpenCV)
            screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            # Guardar la imagen
            cv2.imwrite(save_path, screenshot_bgr)
            print(f"Captura guardada en: {save_path}")
            
            return screenshot_bgr
            
        except Exception as e:
            print(f"Error al capturar pantalla: {e}")
            return None
    
    def detect_and_locate_board(self, screenshot_path: str = "sudoku_screenshot.png") -> Optional[Tuple]:
        """
        Detecta el tablero en la captura y calcula sus coordenadas en pantalla.
        
        Args:
            screenshot_path: Ruta de la imagen capturada
            
        Returns:
            Tupla (x, y, w, h) con las coordenadas del tablero o None si falla
        """
        try:
            # Cargar la imagen
            screenshot = cv2.imread(screenshot_path)
            if screenshot is None:
                print("No se pudo cargar la captura de pantalla")
                return None
            
            # Usar el detector para encontrar el tablero
            print("Detectando tablero en la captura...")
            resultados = self.detector.detectar_tablero(screenshot)
            
            if resultados is None or resultados.get("board_area_coords") is None:
                print("No se pudo detectar el tablero")
                return None
            
            # Obtener coordenadas del tablero en la imagen
            board_coords = resultados["board_area_coords"]
            print(f"Tablero detectado en imagen: {board_coords}")
            
            # Guardar las coordenadas
            self.board_region = board_coords
            
            return board_coords
            
        except Exception as e:
            print(f"Error al detectar tablero: {e}")
            return None
    
    def calculate_cell_positions(self) -> Optional[list]:
        """
        Calcula las posiciones en pantalla de cada celda del tablero.
        
        Returns:
            Lista de posiciones (x, y) para cada celda o None si falla
        """
        if self.board_region is None:
            print("Primero detecta el tablero")
            return None
        
        try:
            x, y, w, h = self.board_region
            
            # Calcular dimensiones de cada celda
            cell_width = w // 9
            cell_height = h // 9
            
            # Calcular posición central de cada celda
            cell_positions = []
            
            for row in range(9):
                for col in range(9):
                    # Calcular posición central de la celda
                    cell_x = x + (col * cell_width) + (cell_width // 2)
                    cell_y = y + (row * cell_height) + (cell_height // 2)
                    
                    cell_positions.append((cell_x, cell_y))
            
            # Guardar las posiciones
            self.cell_positions = cell_positions
            
            print(f"Posiciones de celdas calculadas: {len(cell_positions)} celdas")
            
            # Mostrar visualización de posiciones (opcional, para debugging)
            self._visualize_cell_positions(cell_positions)
            
            return cell_positions
            
        except Exception as e:
            print(f"Error al calcular posiciones de celdas: {e}")
            return None
    
    def _visualize_cell_positions(self, cell_positions: list) -> None:
        """
        Muestra una visualización de las posiciones de las celdas.
        Solo para debugging.
        """
        print("Mostrando visualización de posiciones (5 segundos)...")
        
        # Guardar posición actual del mouse
        original_pos = pyautogui.position()
        
        # Mostrar cada posición
        for i, (x, y) in enumerate(cell_positions):
            row, col = divmod(i, 9)
            pyautogui.moveTo(x, y, duration=0.1)
            pyautogui.click()
            time.sleep(0.05)
            
            # Escribir coordenadas temporalmente
            pyautogui.typewrite(f"{row+1},{col+1}")
            time.sleep(0.05)
            
            # Borrar
            pyautogui.press('backspace', presses=4)
        
        # Volver a la posición original
        pyautogui.moveTo(original_pos)
        time.sleep(1)
        
        print("Visualización completada")
    
    def solve_and_fill_board(self, screenshot_path: str = "sudoku_screenshot.png") -> bool:
        """
        Proceso completo: detectar, resolver y rellenar el tablero.
        
        Args:
            screenshot_path: Ruta de la imagen capturada
            
        Returns:
            True si se completó exitosamente, False en caso contrario
        """
        try:
            # Paso 1: Obtener grilla del Sudoku
            print("\n=== Paso 1: Detectando Sudoku ===")
            grilla = self.detector.obtener_grilla_final(screenshot_path)
            
            if grilla is None:
                print("No se pudo obtener la grilla del Sudoku")
                return False
            
            print("\nGrilla detectada:")
            print(grilla)
            
            # Paso 2: Resolver el Sudoku
            print("\n=== Paso 2: Resolviendo Sudoku ===")
            solucion = self.detector.resolver_con_pysudoku(grilla)
            
            if solucion is None:
                print("No se pudo resolver el Sudoku")
                return False
            
            print("\nSolución encontrada:")
            print(solucion)
            
            # Paso 3: Calcular diferencia (celdas a rellenar)
            print("\n=== Paso 3: Calculando celdas a rellenar ===")
            diferencia = self.detector.obtener_diferencia(grilla, solucion)
            
            print(f"Celdas a rellenar: {len(diferencia)}")
            for row, col, value in diferencia:
                print(f"  Fila {row+1}, Col {col+1}: {value}")
            
            # Paso 4: Rellenar celdas en el juego
            print("\n=== Paso 4: Rellenando celdas en el juego ===")
            
            if self.cell_positions is None:
                print("Calculando posiciones de celdas...")
                if not self.calculate_cell_positions():
                    print("No se pudieron calcular posiciones de celdas")
                    return False
            
            # Rellenar cada celda vacía
            for row, col, value in diferencia:
                # Calcular índice de la celda
                cell_index = row * 9 + col
                
                if cell_index < len(self.cell_positions):
                    x, y = self.cell_positions[cell_index]
                    
                    # Mover el cursor a la celda
                    pyautogui.moveTo(x, y, duration=0.1)
                    pyautogui.click()
                    
                    # Escribir el valor
                    pyautogui.typewrite(str(value))
                    
                    # Pequeña pausa para evitar sobrecarga
                    time.sleep(0.05)
                    
                    print(f"  Rellenada celda ({row+1}, {col+1}) con {value}")
                else:
                    print(f"  Error: Índice de celda fuera de rango: {cell_index}")
            
            print("\n¡Sudoku completado exitosamente!")
            return True
            
        except Exception as e:
            print(f"Error durante el proceso: {e}")
            return False
    
    def run_full_automation(self, difficulty: str = "easy") -> bool:
        """
        Ejecuta todo el proceso de automatización.
        
        Args:
            difficulty: Dificultad del Sudoku (easy, medium, hard, expert)
            
        Returns:
            True si se completó exitosamente, False en caso contrario
        """
        print("=" * 50)
        print("INICIANDO AUTOMATIZACIÓN DE SUDOKU")
        print("=" * 50)
        
        try:
            # Paso 0: Abrir navegador
            print("\n[Paso 0] Abriendo navegador...")
            if not self.open_browser_and_navigate():
                print("No se pudo abrir el navegador. Continuando con captura de pantalla actual...")
            
            # Dar tiempo para que el usuario ajuste la ventana si es necesario
            print("\nPreparándose para capturar...")
            print("Asegúrate de que el tablero de Sudoku sea visible.")
            print("La captura comenzará en 5 segundos...")
            time.sleep(5)
            
            # Paso 1: Capturar pantalla
            print("\n[Paso 1] Capturando pantalla...")
            screenshot_path = "sudoku_screenshot.png"
            screenshot = self.capture_game_screenshot(screenshot_path)
            
            if screenshot is None:
                print("Error al capturar pantalla")
                return False
            
            # Paso 2: Detectar tablero
            print("\n[Paso 2] Detectando tablero...")
            board_coords = self.detect_and_locate_board(screenshot_path)
            
            if board_coords is None:
                print("No se pudo detectar el tablero. Intentando procesar directamente...")
            
            # Paso 3: Calcular posiciones de celdas
            print("\n[Paso 3] Calculando posiciones...")
            if not self.calculate_cell_positions():
                print("Advertencia: No se pudieron calcular posiciones exactas")
                print("Intentando con estimaciones...")
                
                # Intentar con estimación basada en la captura
                height, width = screenshot.shape[:2]
                self.board_region = (width//4, height//4, width//2, height//2)
                self.calculate_cell_positions()
            
            # Paso 4: Resolver y rellenar
            print("\n[Paso 4] Resolviendo y rellenando...")
            success = self.solve_and_fill_board(screenshot_path)
            
            if success:
                print("\n" + "=" * 50)
                print("AUTOMATIZACIÓN COMPLETADA EXITOSAMENTE")
                print("=" * 50)
                
                # Opcional: Tomar captura del resultado
                result_path = "sudoku_resultado.png"
                pyautogui.screenshot(result_path)
                print(f"Captura del resultado guardada en: {result_path}")
                
                return True
            else:
                print("\n" + "=" * 50)
                print("AUTOMATIZACIÓN FALLÓ")
                print("=" * 50)
                return False
                
        except KeyboardInterrupt:
            print("\n\nProceso interrumpido por el usuario")
            print("Posición actual del mouse:", pyautogui.position())
            return False
        except Exception as e:
            print(f"\nError inesperado: {e}")
            return False
    
    def calibrate_board_position(self) -> None:
        """
        Herramienta de calibración para encontrar manualmente el tablero.
        Útil cuando la detección automática falla.
        """
        print("\n" + "=" * 50)
        print("HERRAMIENTA DE CALIBRACIÓN")
        print("=" * 50)
        print("\nInstrucciones:")
        print("1. Mueve el mouse a la esquina superior izquierda del tablero")
        print("2. Presiona 's' para guardar esa posición")
        print("3. Mueve el mouse a la esquina inferior derecha del tablero")
        print("4. Presiona 'e' para guardar y calcular")
        print("5. Presiona 'q' para salir")
        print("\nEsperando entrada...")
        
        corners = []
        
        try:
            while True:
                # Mostrar posición actual
                x, y = pyautogui.position()
                print(f"Posición actual: ({x}, {y})", end='\r')
                
                # Esperar entrada del teclado
                if pyautogui.isPressed('s'):
                    corners.append((x, y))
                    print(f"\nEsquina superior izquierda guardada: ({x}, {y})")
                    time.sleep(0.5)
                
                elif pyautogui.isPressed('e') and len(corners) >= 1:
                    corners.append((x, y))
                    print(f"\nEsquina inferior derecha guardada: ({x}, {y})")
                    
                    # Calcular región del tablero
                    x1, y1 = corners[0]
                    x2, y2 = corners[1]
                    
                    self.board_region = (x1, y1, x2-x1, y2-y1)
                    print(f"\nRegión del tablero calculada: {self.board_region}")
                    
                    # Calcular posiciones de celdas
                    self.calculate_cell_positions()
                    break
                
                elif pyautogui.isPressed('q'):
                    print("\nCalibración cancelada")
                    break
                    
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nCalibración interrumpida")


def main():
    """Función principal"""
    
    # Crear instancia del solucionador automático
    solver = SudokuAutoSolver()
    
    print("\n" + "=" * 50)
    print("SUDOKU AUTO SOLVER - MENÚ PRINCIPAL")
    print("=" * 50)
    print("\nOpciones:")
    print("1. Ejecutar automatización completa")
    print("2. Solo detectar y mostrar solución (sin rellenar)")
    print("3. Calibrar posición del tablero manualmente")
    print("4. Probar detección con captura existente")
    print("5. Salir")
    
    choice = input("\nSelecciona una opción (1-5): ").strip()
    
    if choice == "1":
        # Ejecutar automatización completa
        print("\nIniciando automatización completa...")
        success = solver.run_full_automation()
        
        if success:
            print("\nEl Sudoku ha sido resuelto automáticamente.")
        else:
            print("\nHubo un error durante la automatización.")
    
    elif choice == "2":
        # Solo detectar y mostrar solución
        print("\nTomando captura de pantalla...")
        screenshot_path = "sudoku_test.png"
        solver.capture_game_screenshot(screenshot_path)
        
        print("\nDetectando y resolviendo...")
        detector = SudokuBoardDetector()
        grilla = detector.obtener_grilla_final(screenshot_path)
        
        if grilla is not None:
            solucion = detector.resolver_con_pysudoku(grilla)
            if solucion is not None:
                print("\nSolución encontrada:")
                print(solucion)
    
    elif choice == "3":
        # Calibrar manualmente
        solver.calibrate_board_position()
    
    elif choice == "4":
        # Probar con captura existente
        test_image = input("Ruta de la imagen de prueba (o Enter para usar captura): ").strip()
        
        if not test_image:
            solver.capture_game_screenshot()
            test_image = "sudoku_screenshot.png"
        
        if os.path.exists(test_image):
            print("\nProcesando imagen...")
            detector = SudokuBoardDetector()
            grilla = detector.obtener_grilla_final(test_image)
            
            if grilla is not None:
                solucion = detector.resolver_con_pysudoku(grilla)
                
                if solucion is not None:
                    print("\nSolución:")
                    print(solucion)
                    
                    # Mostrar diferencia
                    diferencia = detector.obtener_diferencia(grilla, solucion)
                    print(f"\nCeldas a rellenar: {len(diferencia)}")
        else:
            print(f"Archivo no encontrado: {test_image}")
    
    elif choice == "5":
        print("Saliendo...")
        return
    
    else:
        print("Opción no válida")
    
    print("\nPresiona Enter para salir...")
    input()


if __name__ == "__main__":
    # Verificar dependencias
    try:
        import pyautogui
        import cv2
        import numpy as np
    except ImportError as e:
        print(f"Error: Falta una dependencia: {e}")
        print("Instala las dependencias con: pip install pyautogui opencv-python numpy")
        sys.exit(1)
    
    # Ejecutar menú principal
    main()