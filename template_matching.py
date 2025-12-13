import cv2
import numpy as np
import os
from typing import Optional

def preprocess_image(image_path: str, invert: bool = False) -> Optional[np.ndarray]:
    """
    Carga, convierte a escala de grises y binariza una imagen.
    
    Args:
        image_path: Ruta al archivo de imagen.
        invert: Si es True, invierte la binarización.

    Returns:
        np.ndarray: Imagen binarizada o None si falla la carga.
    """
    if not os.path.exists(image_path):
        print(f"[ERROR] Archivo no encontrado: {image_path}")
        return None
        
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    if img is None:
        print(f"[ERROR] No se pudo cargar la imagen: {image_path}")
        return None

    # Umbralización fija
    threshold_type = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY
    _, binary_img = cv2.threshold(img, 150, 255, threshold_type)
    
    return binary_img


def run_template_matching(image_path: str, template_path: str):
    """
    Realiza Template Matching de un template en una imagen de origen y 
    recuadra todas las veces que la coincidencia supera el umbral.
    """
    print(f"[INFO] Procesando imagen: {image_path} y template: {template_path}")
    
    # Preprocesamiento de ambas imágenes
    img_source_bn = preprocess_image(image_path, invert=False)
    img_template_bn = preprocess_image(template_path, invert=False)

    if img_source_bn is None or img_template_bn is None:
        print("[ERROR] Falló el preprocesamiento de una o ambas imágenes. Terminando.")
        return

    # Usar la imagen original a color para dibujar el resultado
    img_display = cv2.imread(image_path)
    if img_display is None:
         img_display = cv2.cvtColor(img_source_bn, cv2.COLOR_GRAY2BGR)

    h, w = img_template_bn.shape[:2]

    # --- Aplicar Template Matching ---
    resultado = cv2.matchTemplate(img_source_bn, img_template_bn, cv2.TM_CCOEFF_NORMED)
    
    # 1. Definir el Umbral de Aceptación
    UMBRAL = 0.82 

    # 2. Obtener todas las ubicaciones
    loc = np.where(resultado >= UMBRAL)
    
    coordenadas_encontradas = 0
    
    # Iterar sobre las coordenadas encontradas (x, y)
    for pt in zip(*loc[::-1]):
        bottom_right = (pt[0] + w, pt[1] + h)
        cv2.rectangle(img_display, pt, bottom_right, (0, 255, 0), 2) # Verde
        coordenadas_encontradas += 1

    # 3. Mostrar el resultado final
    if coordenadas_encontradas > 0:
        print(f"\n[RESULTADO] Se encontraron {coordenadas_encontradas} coincidencias con un umbral de {UMBRAL}.")
    else:
        # En caso de no encontrar nada, obtener la mejor coincidencia para información
        _, max_val, _, _ = cv2.minMaxLoc(resultado)
        cv2.putText(img_display, f"No hay coincidencias > {UMBRAL}. Max: {max_val:.2f}", (20, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        print(f"\n[RESULTADO] No se encontraron coincidencias con umbral >= {UMBRAL}. Máximo valor: {max_val:.4f}")


    # Mostrar la imagen
    cv2.imshow("Template Matching - Multiples Coincidencias", img_display)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# --- Ejemplo de Uso ---
if __name__ == '__main__':
    for n in range(1,10):
        template_path = f'./templates/{n}.png'
        image_path = './templates/celdas.png'
        
        RUTAS_EJEMPLO = {
            "IMAGE": image_path, # Imagen donde buscar
            "TEMPLATE": template_path   # Imagen a buscar (la del dígito)
        }

        run_template_matching(RUTAS_EJEMPLO["IMAGE"], RUTAS_EJEMPLO["TEMPLATE"])

