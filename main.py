import cv2
import numpy as np
import pytesseract
from typing import List, Tuple, Optional, Dict

class SudokuBoardDetector:
    """
    Clase para detectar, segmentar y reconocer la grilla 9x9 de un tablero de Sudoku
    a partir de una imagen.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        # ... (código __init__ sin cambios) ...
        self.config = config if config is not None else {}
        self.GRID_SIZE = 9
        self.TESSERACT_CONFIG = r'--oem 3 --psm 10 -c tessedit_char_whitelist=123456789'
        
        # Si Tesseract no está en el PATH, debe configurarse aquí:
        # pytesseract.pytesseract.tesseract_cmd = r'/ruta/a/tesseract.exe'


    # Suponiendo que está usando la clase SudokuBoardDetector

    def detectar_tablero(self, imagen: np.ndarray) -> Optional[Dict]:
        """
        1. Preprocesa la imagen.
        2. Selecciona el contorno del tablero 9x9 (el cuadrado más grande).
        3. Identifica los 9 bloques 3x3 dentro del tablero.
        4. Visualiza los resultados (tablero en ROJO, sub-grillas en AZUL).
        5. Retorna un diccionario con la ROI y los datos de las áreas detectadas.
        """
        print("[Paso 1] Buscando la ROI y las sub-grillas...")
        
        # 1. Aplicar preprocesamiento
        imagen_procesada = self._preparar_imagen(imagen)
        
        # 2. Encontrar contornos
        contornos, _ = cv2.findContours(imagen_procesada, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Inicializar variables de búsqueda
        contorno_tablero_optimo = None
        max_area = 0
        
        # Copia para visualizar
        imagen_vis = imagen.copy() 
        
        # 3. Seleccionar el contorno del tablero 9x9 (el más grande y cuadrado)
        for contorno in contornos:
            area = cv2.contourArea(contorno)
            x, y, w, h = cv2.boundingRect(contorno)
            aspect_ratio = float(w) / h
            
            # Criterios para el tablero principal (gran tamaño, cuadrado)
            # El umbral de área DEBE ajustarse al tamaño de su imagen.
            if area > 10000 and 0.9 <= aspect_ratio <= 1.1: 
                if area > max_area:
                    max_area = area
                    contorno_tablero_optimo = contorno

        resultados = {
            "roi_tablero": None,
            "board_area_coords": None,
            "sub_grids_coords": [] # Lista para los 9 bloques 3x3
        }

        if contorno_tablero_optimo is not None:
            x, y, w, h = cv2.boundingRect(contorno_tablero_optimo)
            
            # Guardar coordenadas del tablero principal
            resultados["board_area_coords"] = (x, y, w, h)
            
            # Retorna la sub-imagen (ROI) para el siguiente paso de segmentación de números
            roi_tablero = imagen[y:y+h, x:x+w]
            resultados["roi_tablero"] = roi_tablero

            # 4. Dibujar el contorno OPTIMO en ROJO
            cv2.drawContours(imagen_vis, [contorno_tablero_optimo], 0, (0, 0, 255), 3)

            # --- Detección de las 9 Sub-Grillas (Bloques 3x3) ---
            
            # La dificultad de buscar los 9 bloques con contornos es que las líneas 
            # de la grilla pueden ser más gruesas para estos, pero también pueden ser
            # contornos de los números. 
            
            # Simplificación: Asumiremos que los 9 bloques son los 9 cuadrados más grandes
            # después del tablero principal, O que la segmentación geométrica es más robusta.
            
            # Para este TEST, buscamos otros contornos cuadrados grandes que estén DENTRO del tablero
            
            contornos_bloque = []
            
            # Iteramos de nuevo sobre todos los contornos para encontrar las 9 sub-grillas
            for contorno in contornos:
                area = cv2.contourArea(contorno)
                x_c, y_c, w_c, h_c = cv2.boundingRect(contorno)
                aspect_ratio_c = float(w_c) / h_c
                
                # Criterios para Sub-Grillas (Bloques 3x3):
                # a) Debe estar contenido dentro del contorno principal.
                # b) Debe ser un cuadrado (0.9 <= aspect_ratio <= 1.1).
                # c) El área debe ser aproximadamente 1/9 del área total (ej. 8% a 15%).
                
                if (x <= x_c and y <= y_c and x + w >= x_c + w_c and y + h >= y_c + h_c):
                    if 0.9 <= aspect_ratio_c <= 1.1:
                        # Si el área es al menos 1/12 del área total (ajustar umbral)
                        if area > max_area / 12.0 and area < max_area * 0.9: 
                            contornos_bloque.append(contorno)
                            
            # 5. Pintar y guardar los resultados de las sub-grillas
            if contornos_bloque:
                # Ordenar por tamaño y tomar los 9 (o el número máximo encontrado)
                contornos_bloque.sort(key=cv2.contourArea, reverse=True)
                
                # Seleccionar los 9 contornos más grandes (o menos si no se encontraron 9)
                contornos_bloque_final = contornos_bloque[:9] 
                
                for contorno_bloque in contornos_bloque_final:
                    x_b, y_b, w_b, h_b = cv2.boundingRect(contorno_bloque)
                    
                    # Dibujar en AZUL (255, 0, 0)
                    cv2.rectangle(imagen_vis, (x_b, y_b), (x_b + w_b, y_b + h_b), (255, 0, 0), 2)
                    
                    # Guardar coordenadas de la sub-grilla
                    resultados["sub_grids_coords"].append((x_b, y_b, w_b, h_b))

            # 6. Visualización Final
            cv2.imshow("Tablero y Sub-Grillas Detectados (Rojo=Tablero, Azul=Bloques)", imagen_vis)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
            return resultados
        
        # Si no se encontró el contorno óptimo
        else:
            print("[ERROR] No se pudo encontrar un contorno de tablero principal con criterios adecuados.")
            cv2.imshow("No se detecto Tablero", imagen_vis)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return None

    def _preparar_imagen(self, imagen: np.ndarray) -> np.ndarray:
        # ... (código _preparar_imagen sin cambios) ...
        gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        # Umbralización Adaptativa para manejar diferentes iluminaciones
        binaria = cv2.adaptiveThreshold(
            gris, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )
        return binaria

    def segmentar_celdas(self, roi_tablero: np.ndarray) -> List[np.ndarray]:
        # ... (código segmentar_celdas sin cambios) ...
        print("[Paso 2] Segmentando 81 celdas...")
        h, w = roi_tablero.shape[:2]
        
        celdas = []
        cell_w = w // self.GRID_SIZE
        cell_h = h // self.GRID_SIZE
        
        for r in range(self.GRID_SIZE):
            for c in range(self.GRID_SIZE):
                # Calcular límites de la celda
                y_min = r * cell_h
                y_max = (r + 1) * cell_h
                x_min = c * cell_w
                x_max = (c + 1) * cell_w
                
                # Extraer la imagen de la celda
                celda_img = roi_tablero[y_min:y_max, x_min:x_max]
                celdas.append(celda_img)
                
        return celdas

    def reconocer_digito(self, celda_img: np.ndarray) -> int:
        # ... (código reconocer_digito sin cambios) ...
        # 1. Comprobar si la celda está vacía ( placeholder )
        # Por ejemplo, contar píxeles no blancos en el centro de la celda
        if np.count_nonzero(celda_img[10:-10, 10:-10]) < 50:
             return 0
        
        # 2. Aplicar OCR (Tesseract)
        try:
            texto = pytesseract.image_to_string(
                celda_img, 
                config=self.TESSERACT_CONFIG
            )
            
            # Limpiar y convertir a entero
            digito_str = texto.strip().replace('\n', '')
            if digito_str.isdigit():
                return int(digito_str[0])
            
        except Exception as e:
            # print(f"Error OCR: {e}") # Para debugging
            pass
            
        # Si no se pudo reconocer o está vacío/ruido
        return 0

    def obtener_grilla_final(self, imagen_path: str) -> Optional[np.ndarray]:
        """
        Orquesta el proceso completo para obtener la matriz 9x9 del Sudoku.
        
        Flujo:
        1. Carga la imagen.
        2. Detecta el tablero principal y las 9 sub-grillas (usa detecta_tablero).
        3. Segmenta la ROI del tablero en 81 celdas (usa segmentar_celdas).
        4. Reconoce el dígito en cada celda (usa reconocer_digito).
        5. Construye y retorna la matriz 9x9 final.
        """
        imagen = cv2.imread(imagen_path)
        if imagen is None:
            print(f"[ERROR] No se pudo cargar la imagen: {imagen_path}")
            return None
        
        # 1. Detectar y aislar el tablero (Retorna un Dict con "roi_tablero")
        # Aquí se ejecuta la lógica de contornos ROJOS y AZULES
        resultados_deteccion = self.detectar_tablero(imagen)
        
        if resultados_deteccion is None or resultados_deteccion.get("roi_tablero") is None:
            print("[ERROR] No se pudo detectar el tablero de Sudoku o la ROI es nula.")
            # La visualización y error ya fue manejada dentro de detectar_tablero
            return None
            
        # Extraer la ROI del tablero (sub-imagen de la grilla 9x9)
        roi_tablero = resultados_deteccion["roi_tablero"]
        
        # Opcional: Si la ROI del tablero no es gris, convertirla a escala de grises
        # para que segmentar_celdas y reconocer_digito funcionen correctamente
        if len(roi_tablero.shape) == 3:
             roi_tablero_gris = cv2.cvtColor(roi_tablero, cv2.COLOR_BGR2GRAY)
        else:
             roi_tablero_gris = roi_tablero

        # 2. Segmentar las 81 celdas (usa segmentación geométrica)
        celdas_img_list = self.segmentar_celdas(roi_tablero_gris)
        
        # 3. Reconocer los dígitos y construir la grilla
        grilla = np.zeros((self.GRID_SIZE, self.GRID_SIZE), dtype=int)
        
        print("[Paso 3] Reconociendo dígitos...")
        for i, celda_img in enumerate(celdas_img_list):
            r, c = divmod(i, self.GRID_SIZE)
            
            # NOTA: Para aumentar la robustez de OCR, la imagen de la celda
            # debe preprocesarse localmente (ej. binarización, centrado)
            
            digito = self.reconocer_digito(celda_img)
            grilla[r, c] = digito
            
            # Opcional: Dibujar el resultado del dígito en la imagen para depuración
            # Se podría dibujar en una copia del roi_tablero para ver la precisión del OCR
            
        print("[OK] Grilla obtenida con éxito.")
        return grilla

# --- Ejemplo de Uso ---
if __name__ == '__main__':
    detector = SudokuBoardDetector()
#      Reemplace 'path/to/sudoku_image.png' con una ruta de prueba
    grilla_resultante = detector.obtener_grilla_final('./facil_1.png') 
    
    # Si grilla_resultante es None, es porque la función detectó y se detuvo
    if grilla_resultante is not None:
        print(grilla_resultante)