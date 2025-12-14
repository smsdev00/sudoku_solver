from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
from typing import List, Optional
import logging
import time
import sys
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Añadir el directorio actual al path para importar main.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar la clase SudokuBoardDetector de main.py
try:
    from main import SudokuBoardDetector
    SUDOKU_DETECTOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"No se pudo importar SudokuBoardDetector: {e}")
    SUDOKU_DETECTOR_AVAILABLE = False

# Importar py-sudoku como alternativa
try:
    from sudoku import Sudoku
    PY_SUDOKU_AVAILABLE = True
except ImportError:
    PY_SUDOKU_AVAILABLE = False
    logger.warning("py-sudoku no está disponible, usando algoritmo propio")

# Crear aplicación FastAPI
app = FastAPI(title="Sudoku Solver API", version="2.0.0")

# Configurar CORS para permitir peticiones desde Tampermonkey
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes para desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de datos
class SudokuGrid(BaseModel):
    grid: List[List[int]]

class SudokuSolution(BaseModel):
    solved: bool
    solution: Optional[List[List[int]]] = None
    message: str = ""
    steps: int = 0
    time_ms: float = 0
    method: str = ""

class SudokuImageRequest(BaseModel):
    image_path: str

# Algoritmo de backtracking puro para la API
class APISudokuSolver:
    def __init__(self):
        self.steps = 0
        
    def solve(self, grid: List[List[int]]) -> Optional[List[List[int]]]:
        """Resuelve un Sudoku usando backtracking"""
        self.steps = 0
        board = [row[:] for row in grid]
        
        def find_empty(board):
            for i in range(9):
                for j in range(9):
                    if board[i][j] == 0:
                        return i, j
            return None, None
        
        def is_valid(board, row, col, num):
            # Verificar fila
            for i in range(9):
                if board[row][i] == num:
                    return False
            
            # Verificar columna
            for i in range(9):
                if board[i][col] == num:
                    return False
            
            # Verificar subcuadrícula 3x3
            box_row = (row // 3) * 3
            box_col = (col // 3) * 3
            for i in range(3):
                for j in range(3):
                    if board[box_row + i][box_col + j] == num:
                        return False
            
            return True
        
        def solve_recursive(board):
            self.steps += 1
            row, col = find_empty(board)
            
            if row is None:
                return True
            
            for num in range(1, 10):
                if is_valid(board, row, col, num):
                    board[row][col] = num
                    
                    if solve_recursive(board):
                        return True
                    
                    board[row][col] = 0
            
            return False
        
        if solve_recursive(board):
            return board
        return None

# Endpoints
@app.get("/")
def read_root():
    return {
        "message": "Sudoku Solver API v2.0",
        "version": "2.0.0",
        "features": {
            "solve_grid": "Resuelve una grilla 9x9",
            "solve_image": "Procesa y resuelve una imagen de Sudoku"
        },
        "available_backends": {
            "sudoku_detector": SUDOKU_DETECTOR_AVAILABLE,
            "py_sudoku": PY_SUDOKU_AVAILABLE
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/solve", response_model=SudokuSolution)
def solve_sudoku(sudoku: SudokuGrid):
    """Resuelve una grilla de Sudoku 9x9"""
    try:
        start_time = time.time()
        
        # Validar la grilla
        if len(sudoku.grid) != 9:
            raise HTTPException(status_code=400, detail="La grilla debe tener 9 filas")
        
        for i, row in enumerate(sudoku.grid):
            if len(row) != 9:
                raise HTTPException(status_code=400, detail=f"La fila {i} debe tener 9 columnas")
            for j, val in enumerate(row):
                if not isinstance(val, int) or val < 0 or val > 9:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Valor inválido en posición ({i},{j}): {val}"
                    )
        
        # Contar celdas con pistas
        filled_cells = sum(1 for row in sudoku.grid for cell in row if cell != 0)
        logger.info(f"Celdas con pistas: {filled_cells}/81")
        
        # Intentar usar py-sudoku si está disponible
        if PY_SUDOKU_AVAILABLE:
            try:
                puzzle = Sudoku(3, 3, board=sudoku.grid)
                if puzzle.validate():
                    solved_puzzle = puzzle.solve()
                    if solved_puzzle:
                        end_time = time.time()
                        return SudokuSolution(
                            solved=True,
                            solution=solved_puzzle.board,
                            message="Resuelto con py-sudoku",
                            steps=0,  # py-sudoku no provee contador de pasos
                            time_ms=(end_time - start_time) * 1000,
                            method="py_sudoku"
                        )
            except Exception as e:
                logger.warning(f"py-sudoku falló: {e}")
        
        # Usar algoritmo propio como fallback
        solver = APISudokuSolver()
        solution = solver.solve(sudoku.grid)
        
        end_time = time.time()
        
        if solution:
            return SudokuSolution(
                solved=True,
                solution=solution,
                message="Resuelto con backtracking",
                steps=solver.steps,
                time_ms=(end_time - start_time) * 1000,
                method="backtracking"
            )
        else:
            return SudokuSolution(
                solved=False,
                message="No se pudo resolver el Sudoku",
                steps=solver.steps,
                time_ms=(end_time - start_time) * 1000,
                method="backtracking"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.post("/solve_image", response_model=SudokuSolution)
def solve_sudoku_image(request: SudokuImageRequest):
    """Procesa una imagen de Sudoku y la resuelve"""
    if not SUDOKU_DETECTOR_AVAILABLE:
        raise HTTPException(
            status_code=501, 
            detail="Funcionalidad de imagen no disponible (SudokuBoardDetector no encontrado)"
        )
    
    try:
        start_time = time.time()
        
        # Verificar que la imagen existe
        if not os.path.exists(request.image_path):
            raise HTTPException(status_code=404, detail="Imagen no encontrada")
        
        # Usar SudokuBoardDetector para procesar la imagen
        detector = SudokuBoardDetector()
        
        # Obtener la grilla desde la imagen
        grid_result = detector.obtener_grilla_final(request.image_path)
        
        if grid_result is None:
            return SudokuSolution(
                solved=False,
                message="No se pudo detectar el Sudoku en la imagen",
                time_ms=(time.time() - start_time) * 1000,
                method="image_processing"
            )
        
        # Resolver la grilla detectada
        grid_list = grid_result.tolist()
        
        # Usar py-sudoku si está disponible
        if PY_SUDOKU_AVAILABLE:
            try:
                puzzle = Sudoku(3, 3, board=grid_list)
                if puzzle.validate():
                    solved_puzzle = puzzle.solve()
                    if solved_puzzle:
                        end_time = time.time()
                        return SudokuSolution(
                            solved=True,
                            solution=solved_puzzle.board,
                            message="Sudoku detectado y resuelto",
                            steps=0,
                            time_ms=(end_time - start_time) * 1000,
                            method="image_processing+py_sudoku"
                        )
            except Exception as e:
                logger.warning(f"py-sudoku falló en solución de imagen: {e}")
        
        # Fallback a algoritmo propio
        solver = APISudokuSolver()
        solution = solver.solve(grid_list)
        
        end_time = time.time()
        
        if solution:
            return SudokuSolution(
                solved=True,
                solution=solution,
                message="Sudoku detectado y resuelto",
                steps=solver.steps,
                time_ms=(end_time - start_time) * 1000,
                method="image_processing+backtracking"
            )
        else:
            return SudokuSolution(
                solved=False,
                message="Sudoku detectado pero no se pudo resolver",
                steps=solver.steps,
                time_ms=(end_time - start_time) * 1000,
                method="image_processing"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando imagen: {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando imagen: {str(e)}")

# Ejecutar el servidor
if __name__ == "__main__":
    import uvicorn
    
    print("=" * 50)
    print("Sudoku Solver API v2.0")
    print("=" * 50)
    print(f"SudokuBoardDetector disponible: {SUDOKU_DETECTOR_AVAILABLE}")
    print(f"py-sudoku disponible: {PY_SUDOKU_AVAILABLE}")
    print("Servidor iniciando en http://127.0.0.1:8888")
    print("=" * 50)
    
    uvicorn.run(app, host="127.0.0.1", port=8888, log_level="info")
