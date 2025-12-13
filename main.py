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
        self.config = config if config is not None else {}
        self.GRID_SIZE = 9
        self.templates = self._cargar_templates()
        # Nota: Si Tesseract no está en el PATH, debe configurarse aquí.

    def _cargar_templates(self) -> Dict[int, np.ndarray]:
        """
        Carga y preprocesa las imágenes de los dígitos (templates) para Template Matching.
        Se asume que los archivos se llaman '1.png', '2.png', etc., y están en ./templates/
        """
        templates = {}
        print("[Setup] Cargando templates de dígitos...")
        for i in range(1, self.GRID_SIZE + 1):
            # NOTA: Ajuste la ruta de ser necesario
            template_path = f'./templates/{i}.png' 
            template_img = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
            
            if template_img is None:
                print(f"[ERROR] No se pudo cargar el template: {template_path}. Template Matching fallará.")
                continue

            # Invertir para que el dígito sea NEGRO sobre fondo BLANCO (consistente con el preprocesamiento de celda)
            # Esto es clave: si el template tiene dígito oscuro, debe invertirse aquí o en el preprocesamiento de celda.
            _, template_bin = cv2.threshold(template_img, 120, 255, cv2.THRESH_BINARY_INV)
            template_bin = cv2.bitwise_not(template_bin) 

            # Redimensionar el template es Opcional, pero recomendable si los templates son muy grandes.
            # Por simplicidad, se utiliza la imagen cargada directamente, asumiendo un tamaño razonable.
            templates[i] = template_bin
            
        return templates
    
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

            # 4. Dibujar el contorno OPTIMO en ROJO
            cv2.drawContours(imagen_vis, [contorno_tablero_optimo], 0, (0, 0, 255), 3)

            # --- Detección de las 9 Sub-Grillas (Bloques 3x3) ---
            # (Lógica para encontrar y dibujar contornos AZULES)
            contornos_bloque = []
            for contorno in contornos:
                area = cv2.contourArea(contorno)
                x_c, y_c, w_c, h_c = cv2.boundingRect(contorno)
                aspect_ratio_c = float(w_c) / h_c
                
                # Criterios para Sub-Grillas (debe estar dentro del tablero principal)
                if (x <= x_c and y <= y_c and x + w >= x_c + w_c and y + h >= y_c + h_c):
                    if 0.9 <= aspect_ratio_c <= 1.1:
                        if area > max_area / 12.0 and area < max_area * 0.9: 
                            contornos_bloque.append(contorno)
                            
            # 5. Pintar y guardar los resultados de las sub-grillas
            if contornos_bloque:
                contornos_bloque.sort(key=cv2.contourArea, reverse=True)
                contornos_bloque_final = contornos_bloque[:9] 
                
                for contorno_bloque in contornos_bloque_final:
                    x_b, y_b, w_b, h_b = cv2.boundingRect(contorno_bloque)
                    cv2.rectangle(imagen_vis, (x_b, y_b), (x_b + w_b, y_b + h_b), (255, 0, 0), 2)
                    resultados["sub_grids_coords"].append((x_b, y_b, w_b, h_b))

            # 6. Visualización Final
            cv2.imshow("Tablero y Sub-Grillas Detectados (Rojo=Tablero, Azul=Bloques)", imagen_vis)
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
        """
        Preprocesamiento de la imagen: escala de grises y umbralización adaptativa.
        """
        gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        # THRESH_BINARY_INV: Invertido para que los contornos se detecten en la grilla oscura
        binaria = cv2.adaptiveThreshold(
            gris, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )
        return binaria

    def segmentar_celdas(self, roi_tablero_gris: np.ndarray, 
                         roi_tablero_original: Optional[np.ndarray] = None) -> List[np.ndarray]:
        """
        Divide la imagen del tablero (ROI) en 81 sub-imágenes (celdas) y 
        visualiza los contornos de celda en amarillo.
        """
        print("[Paso 2] Segmentando 81 celdas...")
        h, w = roi_tablero_gris.shape[:2]
        
        celdas = []
        cell_w = w // self.GRID_SIZE
        cell_h = h // self.GRID_SIZE
        
        # Copia para dibujar si se proporciona la imagen original a color
        imagen_vis = roi_tablero_original.copy() if roi_tablero_original is not None else None
        
        for r in range(self.GRID_SIZE):
            for c in range(self.GRID_SIZE):
                # Calcular límites de la celda
                y_min = r * cell_h
                y_max = (r + 1) * cell_h
                x_min = c * cell_w
                x_max = (c + 1) * cell_w
                
                # Extraer la imagen de la celda (usando la versión en GRIS para OCR)
                celda_img = roi_tablero_gris[y_min:y_max, x_min:x_max]
                celdas.append(celda_img)
                
                # --- Visualización de celdas (Amarillo: 0, 255, 255) ---
                if imagen_vis is not None:
                    cv2.rectangle(imagen_vis, (x_min, y_min), (x_max, y_max), (0, 255, 255), 1)

        if imagen_vis is not None:
            cv2.imshow("Segmentacion 81 Celdas (Amarillo)", imagen_vis)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
        return celdas

    def reconocer_digito(self, celda_img: np.ndarray) -> int:
        """
        Aplica Preprocesamiento y luego Template Matching para determinar el número en la celda.
        """
        h, w = celda_img.shape[:2]
        
        # 1. Preprocesamiento: Recortar y Binarizar (Mismo que antes)
        margin = h // 6 
        center_img = celda_img[margin: h - margin, margin: w - margin]
        center_img = cv2.medianBlur(center_img, 3) 
        
        # Dígito BLANCO, Fondo NEGRO.
        _, celda_binarizada = cv2.threshold(center_img, 120, 255, cv2.THRESH_BINARY_INV)

        # 2. Comprobar si la celda está vacía (Mismo que antes)
        if np.count_nonzero(celda_binarizada) < 150: 
            return 0
        
        # 3. Preparar imagen para Template Matching: Negro sobre Blanco (Consistente con templates)
        # El dígito se invierte a NEGRO sobre fondo BLANCO
        celda_match = cv2.bitwise_not(celda_binarizada)
        
        # --- 4. Template Matching ---
        mejor_match = 0
        mejor_digito = 0
        
        for digito, template in self.templates.items():
            # Redimensionar el template para que coincida con la celda (opcional, si los tamaños son fijos)
            # Aquí redimensionamos el template al tamaño de la ROI de la celda.
            template_resized = cv2.resize(template, (celda_match.shape[1], celda_match.shape[0]))
            
            # Aplicar Template Matching. Usamos CCOEFF_NORMED para que la correlación sea entre 0 y 1.
            resultado = cv2.matchTemplate(celda_match, template_resized, cv2.TM_CCOEFF_NORMED)
            
            # Obtener el valor máximo de coincidencia
            _, max_val, _, _ = cv2.minMaxLoc(resultado)
            
            # Se puede mostrar la celda y el match para debug.
            # print(f"Digito {digito}: Match = {max_val:.4f}")
            
            # Actualizar el mejor match
            if max_val > mejor_match:
                mejor_match = max_val
                mejor_digito = digito
                
        # 5. Criterio de Aceptación: Si el mejor match es alto, se acepta el dígito
        # Este umbral puede requerir ajuste (ej. 0.8 para una coincidencia fuerte)
        UMBRAL_ACEPTACION = 0.7 
        
        if mejor_match >= UMBRAL_ACEPTACION:
            return mejor_digito
        else:
            # Si el match es bajo, se considera que no se ha reconocido un dígito válido (podría ser ruido)
            return 0
        
    def obtener_grilla_final(self, imagen_path: str) -> Optional[np.ndarray]:
        """
        Orquesta el proceso completo para obtener la matriz 9x9 del Sudoku.
        """
        imagen = cv2.imread(imagen_path)
        if imagen is None:
            print(f"[ERROR] No se pudo cargar la imagen: {imagen_path}")
            return None
        
        # 1. Detectar y aislar el tablero 
        resultados_deteccion = self.detectar_tablero(imagen)
        
        if resultados_deteccion is None or resultados_deteccion.get("roi_tablero") is None:
            print("[ERROR] No se pudo detectar el tablero de Sudoku o la ROI es nula.")
            return None
            
        roi_tablero = resultados_deteccion["roi_tablero"]
        
        # Preparación para segmentación y OCR
        if len(roi_tablero.shape) == 3:
             roi_tablero_gris = cv2.cvtColor(roi_tablero, cv2.COLOR_BGR2GRAY)
             roi_tablero_original_color = roi_tablero.copy() 
        else:
             roi_tablero_gris = roi_tablero
             roi_tablero_original_color = None

        # 2. Segmentar las 81 celdas (Esto también ejecuta la visualización AMARILLA)
        celdas_img_list = self.segmentar_celdas(roi_tablero_gris, roi_tablero_original_color)
        
        # 3. Reconocer los dígitos y construir la grilla
        grilla = np.zeros((self.GRID_SIZE, self.GRID_SIZE), dtype=int)
        
        print("[Paso 3] Reconociendo dígitos...")
        for i, celda_img in enumerate(celdas_img_list):
            r, c = divmod(i, self.GRID_SIZE)
            
            digito = self.reconocer_digito(celda_img)
            grilla[r, c] = digito
            
        print("[OK] Grilla obtenida con éxito.")
        
        # Mostrar la grilla final
        print("\nGrilla de Sudoku detectada:")
        print(grilla)

        return grilla

# --- Ejemplo de Uso ---
if __name__ == '__main__':
    detector = SudokuBoardDetector()
    grilla_resultante = detector.obtener_grilla_final('./imgs/facil_1.png')