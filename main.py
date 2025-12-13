import cv2
import numpy as np
import os
from typing import List, Tuple, Optional, Dict
from sudoku import Sudoku  # Importar la librería py-sudoku

class SudokuBoardDetector:
    """
    Clase para detectar, segmentar y reconocer la grilla 9x9 de un tablero de Sudoku
    a partir de una imagen. Utiliza Template Matching para el reconocimiento de dígitos.
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config if config is not None else {}
        self.GRID_SIZE = 9
        self.UMBRAL_ACEPTACION = 0.7  # Umbral que funciona en template_matching.py
        # Cargar las plantillas de dígitos al inicializar la clase
        self.templates = self._cargar_templates()

    def _preprocess_image(self, image_path: str, invert: bool = False) -> Optional[np.ndarray]:
        """
        EXACTAMENTE la misma función que en template_matching.py
        Carga, convierte a escala de grises y binariza una imagen.
        """
        if not os.path.exists(image_path):
            print(f"[ERROR] Archivo no encontrado: {image_path}")
            return None

        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        if img is None:
            print(f"[ERROR] No se pudo cargar la imagen: {image_path}")
            return None

        # Umbralización fija IDÉNTICA a template_matching.py
        threshold_type = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY
        _, binary_img = cv2.threshold(img, 150, 255, threshold_type)

        return binary_img

    def _cargar_templates(self) -> Dict[int, np.ndarray]:
        """
        Carga y preprocesa las imágenes de los dígitos (templates) usando EXACTAMENTE
        el mismo preprocesamiento que en template_matching.py
        """
        templates = {}
        print("[Setup] Cargando templates de dígitos...")
        for i in range(1, self.GRID_SIZE + 1):
            template_path = f'./templates/{i}.png'

            # Usar el mismo preprocesamiento que en template_matching.py
            template_img = self._preprocess_image(template_path, invert=False)

            if template_img is None:
                print(f"[ERROR] No se pudo cargar el template: {template_path}. Template Matching fallará.")
                continue

            templates[i] = template_img

        return templates

    def detectar_tablero(self, imagen: np.ndarray) -> Optional[Dict]:
        """ Detecta y retorna la ROI del tablero. """
        print("[Paso 1] Buscando la ROI y las sub-grillas...")

        # 1. Aplicar preprocesamiento
        imagen_procesada = self._preparar_imagen(imagen)

        # 2. Encontrar contornos
        contornos, _ = cv2.findContours(imagen_procesada, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        contorno_tablero_optimo = None
        max_area = 0
        imagen_vis = imagen.copy()

        # 3. Seleccionar el contorno del tablero 9x9
        for contorno in contornos:
            area = cv2.contourArea(contorno)
            x, y, w, h = cv2.boundingRect(contorno)
            aspect_ratio = float(w) / h

            if area > 10000 and 0.9 <= aspect_ratio <= 1.1:
                if area > max_area:
                    max_area = area
                    contorno_tablero_optimo = contorno

        resultados = {
            "roi_tablero": None,
            "board_area_coords": None,
            "sub_grids_coords": []
        }

        if contorno_tablero_optimo is not None:
            x, y, w, h = cv2.boundingRect(contorno_tablero_optimo)

            resultados["board_area_coords"] = (x, y, w, h)
            roi_tablero = imagen[y:y+h, x:x+w]
            resultados["roi_tablero"] = roi_tablero

            cv2.drawContours(imagen_vis, [contorno_tablero_optimo], 0, (0, 0, 255), 3)

            # --- Detección de las 9 Sub-Grillas ---
            contornos_bloque = []
            for contorno in contornos:
                area = cv2.contourArea(contorno)
                x_c, y_c, w_c, h_c = cv2.boundingRect(contorno)
                aspect_ratio_c = float(w_c) / h_c

                if (x <= x_c and y <= y_c and x + w >= x_c + w_c and y + h >= y_c + h_c):
                    if 0.9 <= aspect_ratio_c <= 1.1:
                        if area > max_area / 12.0 and area < max_area * 0.9:
                            contornos_bloque.append(contorno)

            if contornos_bloque:
                contornos_bloque.sort(key=cv2.contourArea, reverse=True)
                contornos_bloque_final = contornos_bloque[:9]

                for contorno_bloque in contornos_bloque_final:
                    x_b, y_b, w_b, h_b = cv2.boundingRect(contorno_bloque)
                    cv2.rectangle(imagen_vis, (x_b, y_b), (x_b + w_b, y_b + h_b), (255, 0, 0), 2)
                    resultados["sub_grids_coords"].append((x_b, y_b, w_b, h_b))

            cv2.imshow("Tablero y Sub-Grillas Detectados", imagen_vis)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

            return resultados

        else:
            print("[ERROR] No se pudo encontrar un contorno de tablero principal con criterios adecuados.")
            cv2.imshow("No se detecto Tablero", imagen_vis)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return None

    def _preparar_imagen(self, imagen: np.ndarray) -> np.ndarray:
        """ Preprocesamiento de la imagen: escala de grises y umbralización adaptativa. """
        gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        binaria = cv2.adaptiveThreshold(
            gris, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )
        return binaria

    def segmentar_celdas(self, roi_tablero_gris: np.ndarray,
                         roi_tablero_original: Optional[np.ndarray] = None) -> List[np.ndarray]:
        """ Divide la imagen del tablero (ROI) en 81 sub-imágenes (celdas). """
        print("[Paso 2] Segmentando 81 celdas...")
        h, w = roi_tablero_gris.shape[:2]

        celdas = []
        cell_w = w // self.GRID_SIZE
        cell_h = h // self.GRID_SIZE

        imagen_vis = roi_tablero_original.copy() if roi_tablero_original is not None else None

        for r in range(self.GRID_SIZE):
            for c in range(self.GRID_SIZE):
                y_min = r * cell_h
                y_max = (r + 1) * cell_h
                x_min = c * cell_w
                x_max = (c + 1) * cell_w

                celda_img = roi_tablero_gris[y_min:y_max, x_min:x_max]
                celdas.append(celda_img)

                if imagen_vis is not None:
                    cv2.rectangle(imagen_vis, (x_min, y_min), (x_max, y_max), (0, 255, 255), 1)

        if imagen_vis is not None:
            cv2.imshow("Segmentacion 81 Celdas", imagen_vis)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return celdas

    def _preprocesar_celda(self, celda_img: np.ndarray) -> np.ndarray:
        """
        Preprocesamiento de celda IDÉNTICO al que funciona en template_matching.py
        """
        # Aplicar el mismo preprocesamiento que en template_matching.py
        # Umbralización fija con 150
        _, binary_celda = cv2.threshold(celda_img, 150, 255, cv2.THRESH_BINARY)

        return binary_celda

    def reconocer_digito(self, celda_img: np.ndarray) -> int:
        """
        Aplica el MISMO Template Matching que funciona en template_matching.py
        """
        # 1. Preprocesar la celda exactamente como en template_matching.py
        celda_preprocesada = self._preprocesar_celda(celda_img)

        # 2. Comprobar si la celda está vacía (similar a template_matching)
        if np.count_nonzero(celda_preprocesada) < 150:
            return 0

        # 3. Template Matching IDÉNTICO a template_matching.py
        mejor_match = 0
        mejor_digito = 0

        for digito, template in self.templates.items():
            h_temp, w_temp = template.shape[:2]

            # Verificar que la celda no sea más pequeña que el template
            if celda_preprocesada.shape[0] < h_temp or celda_preprocesada.shape[1] < w_temp:
                # Redimensionar template para que quepa en la celda
                scale_h = celda_preprocesada.shape[0] / h_temp
                scale_w = celda_preprocesada.shape[1] / w_temp
                scale = min(scale_h, scale_w) * 0.8  # Reducir un poco para margen
                new_h = int(h_temp * scale)
                new_w = int(w_temp * scale)
                template_resized = cv2.resize(template, (new_w, new_h), interpolation=cv2.INTER_AREA)
            else:
                template_resized = template

            # Aplicar Template Matching
            resultado = cv2.matchTemplate(celda_preprocesada, template_resized, cv2.TM_CCOEFF_NORMED)

            # Encontrar el máximo valor
            _, max_val, _, _ = cv2.minMaxLoc(resultado)

            if max_val > mejor_match:
                mejor_match = max_val
                mejor_digito = digito

        # 4. Aplicar el mismo umbral de aceptación
        if mejor_match >= self.UMBRAL_ACEPTACION:
            return mejor_digito
        else:
            return 0

    def obtener_grilla_final(self, imagen_path: str) -> Optional[np.ndarray]:
        """ Orquesta el proceso completo para obtener la matriz 9x9 del Sudoku. """
        imagen = cv2.imread(imagen_path)
        if imagen is None:
            print(f"[ERROR] No se pudo cargar la imagen: {imagen_path}")
            return None

        if len(imagen.shape) == 2:
            imagen = cv2.cvtColor(imagen, cv2.COLOR_GRAY2BGR)

        resultados_deteccion = self.detectar_tablero(imagen)

        if resultados_deteccion is None or resultados_deteccion.get("roi_tablero") is None:
            print("[ERROR] No se pudo detectar el tablero de Sudoku o la ROI es nula.")
            return None

        roi_tablero = resultados_deteccion["roi_tablero"]

        if len(roi_tablero.shape) == 3:
             roi_tablero_gris = cv2.cvtColor(roi_tablero, cv2.COLOR_BGR2GRAY)
             roi_tablero_original_color = roi_tablero.copy()
        else:
             roi_tablero_gris = roi_tablero
             roi_tablero_original_color = None

        celdas_img_list = self.segmentar_celdas(roi_tablero_gris, roi_tablero_original_color)

        grilla = np.zeros((self.GRID_SIZE, self.GRID_SIZE), dtype=int)

        print("[Paso 3] Reconociendo dígitos...")
        for i, celda_img in enumerate(celdas_img_list):
            r, c = divmod(i, self.GRID_SIZE)

            digito = self.reconocer_digito(celda_img)
            grilla[r, c] = digito

        print("[OK] Grilla obtenida con éxito.")
        print("\nGrilla de Sudoku detectada:")
        print(grilla)

        return grilla

    def resolver_con_pysudoku(self, grilla: np.ndarray) -> Optional[np.ndarray]:
        """
        Resuelve el Sudoku usando la librería py-sudoku.

        Args:
            grilla: Array 9x9 con 0 en celdas vacías

        Returns:
            Array 9x9 resuelto o None si no tiene solución
        """
        try:
            # Convertir el array numpy a lista de listas
            board = grilla.tolist()

            # Crear un objeto Sudoku con la grilla detectada
            puzzle = Sudoku(3, 3, board=board)

            # Verificar si el puzzle es válido
            if not puzzle.validate():
                print("[ERROR] El Sudoku detectado no es válido")
                return None

            # Resolver el puzzle
            solved = puzzle.solve()

            if solved:
                # Obtener la grilla resuelta como array numpy
                grilla_resuelta = np.array(solved.board)
                return grilla_resuelta
            else:
                print("[ERROR] No se pudo resolver el Sudoku")
                return None

        except Exception as e:
            print(f"[ERROR] Error al resolver con py-sudoku: {e}")
            return None

    def resolver_y_mostrar(self, imagen_path: str) -> Optional[np.ndarray]:
        """
        Proceso completo: detectar, reconocer y resolver Sudoku usando py-sudoku.

        Args:
            imagen_path: Ruta a la imagen del Sudoku

        Returns:
            Array 9x9 resuelto o None si falla
        """
        # 1. Obtener grilla del Sudoku
        grilla_detectada = self.obtener_grilla_final(imagen_path)

        if grilla_detectada is None:
            return None

        print("\n[Grilla detectada (0 = vacío):]")
        print(grilla_detectada)

        # 2. Resolver el Sudoku con py-sudoku
        print("\n[Resolviendo con py-sudoku...]")
        grilla_resuelta = self.resolver_con_pysudoku(grilla_detectada)

        if grilla_resuelta is not None:
            print("\n[Grilla resuelta con py-sudoku:]")
            print(grilla_resuelta)

            # Mostrar comparación
            print("\n[Comparación:]")
            for i in range(9):
                fila_detectada = " ".join(str(x) if x != 0 else "." for x in grilla_detectada[i])
                fila_resuelta = " ".join(str(x) for x in grilla_resuelta[i])
                print(f"Fila {i+1}: {fila_detectada}   ->   {fila_resuelta}")

        return grilla_resuelta

    def obtener_diferencia(self, original: np.ndarray, resuelta: np.ndarray) -> List[Tuple[int, int, int]]:
        """
        Obtiene las celdas que fueron llenadas por el solver.

        Args:
            original: Grilla original (con 0 en vacíos)
            resuelta: Grilla resuelta

        Returns:
            Lista de tuplas (fila, col, valor) con las celdas llenadas
        """
        diferencia = []
        for i in range(9):
            for j in range(9):
                if original[i, j] == 0 and resuelta[i, j] != 0:
                    diferencia.append((i, j, resuelta[i, j]))
        return diferencia

    def visualizar_solucion(self, imagen_path: str, output_path: Optional[str] = None) -> Optional[np.ndarray]:
        """
        Visualiza la solución superpuesta en la imagen original.

        Args:
            imagen_path: Ruta a la imagen del Sudoku
            output_path: Ruta para guardar la imagen resultante (opcional)

        Returns:
            Imagen con la solución superpuesta
        """
        # Cargar la imagen original
        imagen_original = cv2.imread(imagen_path)
        if imagen_original is None:
            print(f"[ERROR] No se pudo cargar la imagen: {imagen_path}")
            return None

        # Obtener la grilla detectada y resuelta
        grilla_detectada = self.obtener_grilla_final(imagen_path)
        if grilla_detectada is None:
            return None

        grilla_resuelta = self.resolver_con_pysudoku(grilla_detectada)
        if grilla_resuelta is None:
            return None

        # Detectar el tablero para obtener sus coordenadas
        resultados_deteccion = self.detectar_tablero(imagen_original)
        if resultados_deteccion is None:
            return None

        x, y, w, h = resultados_deteccion["board_area_coords"]

        # Crear una copia para dibujar
        imagen_resultado = imagen_original.copy()

        # Calcular dimensiones de cada celda
        cell_w = w // 9
        cell_h = h // 9

        # Dibujar los números de la solución en las celdas vacías
        for i in range(9):
            for j in range(9):
                if grilla_detectada[i, j] == 0:  # Solo dibujar en celdas vacías
                    # Calcular posición del texto
                    text_x = x + j * cell_w + cell_w // 3
                    text_y = y + i * cell_h + 2 * cell_h // 3

                    # Dibujar el número de la solución
                    numero = str(grilla_resuelta[i, j])
                    cv2.putText(imagen_resultado, numero,
                               (text_x, text_y),
                               cv2.FONT_HERSHEY_SIMPLEX,
                               0.8, (0, 0, 255), 2)  # Rojo para la solución

        # Dibujar un rectángulo alrededor del tablero
        cv2.rectangle(imagen_resultado, (x, y), (x + w, y + h), (0, 255, 0), 3)

        # Mostrar la imagen
        cv2.imshow("Sudoku Resuelto", imagen_resultado)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # Guardar la imagen si se especifica una ruta de salida
        if output_path:
            cv2.imwrite(output_path, imagen_resultado)
            print(f"[INFO] Imagen guardada en: {output_path}")

        return imagen_resultado

# --- Ejemplo de Uso ---
if __name__ == '__main__':
    detector = SudokuBoardDetector()

    # Opción 1: Solo obtener la grilla
    grilla_resultante = detector.obtener_grilla_final('./imgs/facil_2.png')

    if grilla_resultante is not None:
        print("\nResultado final (lista de listas):")
        print(grilla_resultante.tolist())

        # Opción 2: Resolver con py-sudoku
        grilla_resuelta = detector.resolver_con_pysudoku(grilla_resultante)
        if grilla_resuelta is not None:
            print("\nSolución (lista de listas):")
            print(grilla_resuelta.tolist())

    # Opción 3: Proceso completo con visualización
    # detector.resolver_y_mostrar('./imgs/facil_1.png')

    # Opción 4: Visualizar solución en la imagen
    # detector.visualizar_solucion('./imgs/facil_1.png', './imgs/solucion.png')
