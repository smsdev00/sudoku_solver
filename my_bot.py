from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
from main import SudokuBoardDetector

# --- Configuración del navegador ---
options = Options()
# options.add_argument("--headless")  # <-- Descomenta si NO quieres ver la ventana del navegador.
driver = webdriver.Chrome(options=options)

try:
    print("[+] Navegando a https://sudoku.com/evil/ ...")
    driver.get("https://sudoku.com/evil/")
    time.sleep(2)
    
    # Acciones de teclado para generar el tablero (si es necesario)
    ActionChains(driver).send_keys(Keys.RIGHT).perform()
    time.sleep(2)
    ActionChains(driver).send_keys(Keys.LEFT).perform()
    time.sleep(2)
    
    print("[+] Tomando captura de toda la pantalla...")
    
    # 1. Capturar TODA la ventana del navegador (sin depender del canvas)
    screenshot_filename = "sudoku_pantalla_completa.png"
    driver.save_screenshot(screenshot_filename)
    print(f"[+] Captura de pantalla completa guardada como: '{screenshot_filename}'")
    
    # --- Procesar la imagen con la lógica existente ---
    print("\n[+] Procesando la imagen para detectar el Sudoku...")
    detector = SudokuBoardDetector()
    
    # Obtener la grilla de números detectada
    grilla_detectada = detector.obtener_grilla_final(screenshot_filename)
    
    if grilla_detectada is None:
        print("[-] No se pudo detectar el tablero en la imagen. Saliendo.")
    else:
        print("\n[+] Grilla detectada (0 = vacío):")
        print(grilla_detectada)
        
        # Resolver el Sudoku usando py-sudoku (integrado en la clase)
        print("\n[+] Resolviendo el Sudoku...")
        grilla_resuelta = detector.resolver_con_pysudoku(grilla_detectada)
        
        if grilla_resuelta is not None:
            print("\n" + "="*50)
            print("[+] ¡SOLUCIÓN ENCONTRADA!")
            print("="*50)
            print(grilla_resuelta)
            print("\n" + "="*50)
        else:
            print("[-] No se pudo resolver el Sudoku (puede que la grilla detectada sea incorrecta).")
            
finally:
    # 2. Cerrar el navegador
    driver.quit()
    print("[+] Navegador cerrado. Proceso finalizado.")