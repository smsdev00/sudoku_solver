// ==UserScript==
// @name         Solucionador de Sudoku con Backtracking
// @namespace    http://tampermonkey.net/
// @version      4.0
// @description  Extrae y resuelve sudokus en sudoku-online.org usando backtracking eficiente
// @author       Asistente de Código
// @match *://*.sudoku-online.org/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=sudoku-online.org
// @grant        GM_addStyle
// ==/UserScript==

(function() {
    'use strict';

    // Agregar estilos CSS
    GM_addStyle(`
        .sudoku-solver-panel {
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            border: 2px solid #4CAF50;
            border-radius: 8px;
            padding: 15px;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            width: 280px;
            font-family: Arial, sans-serif;
        }

        .sudoku-solver-title {
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
            border-bottom: 1px solid #eee;
            padding-bottom: 8px;
            font-size: 16px;
        }

        .sudoku-solver-btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            margin: 5px 0;
            width: 100%;
            font-size: 14px;
            transition: background 0.3s;
        }

        .sudoku-solver-btn:hover {
            background: #45a049;
        }

        .sudoku-solver-btn:disabled {
            background: #cccccc;
            cursor: not-allowed;
        }

        .sudoku-solver-btn.blue {
            background: #2196F3;
        }

        .sudoku-solver-btn.blue:hover {
            background: #1976D2;
        }

        .sudoku-solver-btn.orange {
            background: #FF9800;
        }

        .sudoku-solver-btn.orange:hover {
            background: #F57C00;
        }

        .sudoku-solver-status {
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            border: 1px solid transparent;
            font-size: 13px;
            min-height: 20px;
        }

        .sudoku-solver-success {
            background-color: #dff0d8;
            color: #3c763d;
            border-color: #d6e9c6;
        }

        .sudoku-solver-error {
            background-color: #f2dede;
            color: #a94442;
            border-color: #ebccd1;
        }

        .sudoku-solver-info {
            background-color: #d9edf7;
            color: #31708f;
            border-color: #bce8f1;
        }

        .sudoku-solver-grid {
            display: grid;
            grid-template-columns: repeat(9, 1fr);
            gap: 1px;
            background-color: #333;
            border: 2px solid #333;
            margin: 10px 0;
            width: 100%;
        }

        .sudoku-solver-cell {
            background-color: white;
            text-align: center;
            padding: 3px;
            font-family: monospace;
            font-size: 11px;
            aspect-ratio: 1;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .sudoku-solver-cell.original {
            background-color: #f5f5f5;
            font-weight: bold;
        }

        .sudoku-solver-cell.solved {
            color: #4CAF50;
        }

        .sudoku-solver-stats {
            font-size: 12px;
            color: #666;
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #eee;
        }

        .sudoku-solver-cell.current {
            background-color: #e8f5e9;
            animation: pulse 0.5s;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
    `);

    // ==============================================
    // ALGORITMO DE BACKTRACKING SEGÚN TU CÓDIGO
    // ==============================================

    class SudokuSolver {
        constructor() {
            this.steps = 0;
            this.startTime = 0;
            this.maxDepth = 0;
        }

        // Encontrar la siguiente celda vacía
        nextEmptySpot(board) {
            for (let i = 0; i < 9; i++) {
                for (let j = 0; j < 9; j++) {
                    if (board[i][j] === 0) {
                        return [i, j];
                    }
                }
            }
            return [-1, -1]; // No hay celdas vacías
        }

        // Verificar si un valor es válido en una fila
        checkRow(board, row, value) {
            for (let i = 0; i < 9; i++) {
                if (board[row][i] === value) {
                    return false;
                }
            }
            return true;
        }

        // Verificar si un valor es válido en una columna
        checkColumn(board, column, value) {
            for (let i = 0; i < 9; i++) {
                if (board[i][column] === value) {
                    return false;
                }
            }
            return true;
        }

        // Verificar si un valor es válido en el cuadrado 3x3
        checkSquare(board, row, column, value) {
            const boxRow = Math.floor(row / 3) * 3;
            const boxCol = Math.floor(column / 3) * 3;

            for (let r = 0; r < 3; r++) {
                for (let c = 0; c < 3; c++) {
                    if (board[boxRow + r][boxCol + c] === value) {
                        return false;
                    }
                }
            }
            return true;
        }

        // Combinar todas las verificaciones
        checkValue(board, row, column, value) {
            return this.checkRow(board, row, value) &&
                   this.checkColumn(board, column, value) &&
                   this.checkSquare(board, row, column, value);
        }

        // Función principal de resolución con backtracking
        solve(board) {
            this.steps = 0;
            this.startTime = performance.now();

            // Función recursiva interna
            const solveRecursive = (board) => {
                this.steps++;

                let emptySpot = this.nextEmptySpot(board);
                let row = emptySpot[0];
                let col = emptySpot[1];

                // Si no hay más celdas vacías, hemos terminado
                if (row === -1) {
                    return true;
                }

                // Intentar números del 1 al 9
                for (let num = 1; num <= 9; num++) {
                    if (this.checkValue(board, row, col, num)) {
                        board[row][col] = num;

                        // Actualizar profundidad máxima
                        const filled = this.countFilledCells(board);
                        this.maxDepth = Math.max(this.maxDepth, filled);

                        // Continuar recursivamente
                        if (solveRecursive(board)) {
                            return true;
                        }

                        // Si llegamos aquí, retroceder
                        board[row][col] = 0;
                    }
                }

                return false;
            };

            // Hacer una copia del tablero para no modificar el original
            const boardCopy = JSON.parse(JSON.stringify(board));
            const solved = solveRecursive(boardCopy);

            const endTime = performance.now();

            return {
                solved: solved,
                solution: solved ? boardCopy : null,
                steps: this.steps,
                time: endTime - this.startTime,
                maxDepth: this.maxDepth
            };
        }

        // Versión paso a paso para visualización
        async solveStepByStep(board, callback = null) {
            this.steps = 0;
            this.startTime = performance.now();
            this.maxDepth = 0;

            // Hacer una copia del tablero
            const boardCopy = JSON.parse(JSON.stringify(board));

            // Función recursiva paso a paso
            const solveRecursiveStep = async (board) => {
                this.steps++;

                // Llamar al callback cada 50 pasos para no saturar
                if (callback && this.steps % 50 === 0) {
                    await callback(board, this.steps);
                }

                let emptySpot = this.nextEmptySpot(board);
                let row = emptySpot[0];
                let col = emptySpot[1];

                if (row === -1) {
                    return true;
                }

                for (let num = 1; num <= 9; num++) {
                    if (this.checkValue(board, row, col, num)) {
                        board[row][col] = num;

                        // Actualizar profundidad
                        const filled = this.countFilledCells(board);
                        this.maxDepth = Math.max(this.maxDepth, filled);

                        if (await solveRecursiveStep(board)) {
                            return true;
                        }

                        board[row][col] = 0;
                    }
                }

                return false;
            };

            const solved = await solveRecursiveStep(boardCopy);
            const endTime = performance.now();

            return {
                solved: solved,
                solution: solved ? boardCopy : null,
                steps: this.steps,
                time: endTime - this.startTime,
                maxDepth: this.maxDepth
            };
        }

        // Contar celdas llenas
        countFilledCells(board) {
            let count = 0;
            for (let i = 0; i < 9; i++) {
                for (let j = 0; j < 9; j++) {
                    if (board[i][j] !== 0) {
                        count++;
                    }
                }
            }
            return count;
        }
    }

    // ==============================================
    // FUNCIONES PARA INTERACTUAR CON LA PÁGINA WEB
    // ==============================================

    // Extraer el sudoku de la página
    function extractSudoku() {
        const sudokuGrid = [];

        // Inicializar la grilla 9x9 con ceros
        for (let i = 0; i < 9; i++) {
            sudokuGrid[i] = Array(9).fill(0);
        }

        // Buscar elementos del sudoku
        const sudokuElements = document.querySelectorAll('[id^="sudo_input_"], div[class*="sudo_field"]');

        if (sudokuElements.length === 0) {
            throw new Error("No se encontraron elementos del sudoku. ¿Estás en la página correcta?");
        }

        // Llenar la grilla con los valores encontrados
        sudokuElements.forEach(element => {
            // Obtener coordenadas
            let row, col;

            // Intentar obtener de data-x y data-y
            if (element.hasAttribute('data-x') && element.hasAttribute('data-y')) {
                row = parseInt(element.getAttribute('data-x'));
                col = parseInt(element.getAttribute('data-y'));
            }
            // Intentar obtener del id
            else if (element.id && element.id.startsWith('sudo_input_')) {
                const index = parseInt(element.id.replace('sudo_input_', ''));
                row = Math.floor(index / 9);
                col = index % 9;
            }
            // Intentar obtener de data-index
            else if (element.hasAttribute('data-index')) {
                const index = parseInt(element.getAttribute('data-index'));
                row = Math.floor(index / 9);
                col = index % 9;
            }

            // Obtener el valor
            let value = 0;
            const textContent = element.textContent.trim();
            if (textContent && !isNaN(textContent) && textContent !== '') {
                value = parseInt(textContent, 10);
            }

            // Asignar a la grilla si tenemos coordenadas válidas
            if (row !== undefined && col !== undefined && row >= 0 && row < 9 && col >= 0 && col < 9) {
                sudokuGrid[row][col] = value;
            }
        });

        // Validar que extrajimos algo
        let filledCells = 0;
        for (let i = 0; i < 9; i++) {
            for (let j = 0; j < 9; j++) {
                if (sudokuGrid[i][j] !== 0) {
                    filledCells++;
                }
            }
        }

        if (filledCells < 17) {
            console.warn("Advertencia: Sudoku con muy pocas pistas. Puede tener múltiples soluciones.");
        }

        if (filledCells === 0) {
            throw new Error("No se pudieron extraer valores del sudoku. Verifica la estructura de la página.");
        }

        return sudokuGrid;
    }

    // Mostrar solución en la página
    function displaySolution(originalGrid, solvedGrid) {
        const sudokuElements = document.querySelectorAll('[id^="sudo_input_"], div[class*="sudo_field"]');

        sudokuElements.forEach(element => {
            let row, col;

            // Obtener coordenadas del elemento
            if (element.hasAttribute('data-x') && element.hasAttribute('data-y')) {
                row = parseInt(element.getAttribute('data-x'));
                col = parseInt(element.getAttribute('data-y'));
            } else if (element.id && element.id.startsWith('sudo_input_')) {
                const index = parseInt(element.id.replace('sudo_input_', ''));
                row = Math.floor(index / 9);
                col = index % 9;
            } else if (element.hasAttribute('data-index')) {
                const index = parseInt(element.getAttribute('data-index'));
                row = Math.floor(index / 9);
                col = index % 9;
            }

            // Si tenemos coordenadas válidas
            if (row !== undefined && col !== undefined) {
                const originalValue = originalGrid[row][col];
                const solvedValue = solvedGrid[row][col];

                // Solo actualizar si estaba vacío o diferente
                if (originalValue === 0 || originalValue !== solvedValue) {
                    element.textContent = solvedValue;
                    element.style.color = '#4CAF50';
                    element.style.fontWeight = 'bold';

                    // Agregar clase para resaltar
                    element.classList.add('sudoku-solved');
                }
            }
        });
    }

    // Restaurar sudoku original
    function restoreOriginal(originalGrid) {
        const sudokuElements = document.querySelectorAll('[id^="sudo_input_"], div[class*="sudo_field"]');

        sudokuElements.forEach(element => {
            let row, col;

            if (element.hasAttribute('data-x') && element.hasAttribute('data-y')) {
                row = parseInt(element.getAttribute('data-x'));
                col = parseInt(element.getAttribute('data-y'));
            } else if (element.id && element.id.startsWith('sudo_input_')) {
                const index = parseInt(element.id.replace('sudo_input_', ''));
                row = Math.floor(index / 9);
                col = index % 9;
            } else if (element.hasAttribute('data-index')) {
                const index = parseInt(element.getAttribute('data-index'));
                row = Math.floor(index / 9);
                col = index % 9;
            }

            if (row !== undefined && col !== undefined) {
                const originalValue = originalGrid[row][col];

                if (originalValue === 0) {
                    element.textContent = '';
                } else {
                    element.textContent = originalValue;
                }

                element.style.color = '';
                element.style.fontWeight = '';
                element.classList.remove('sudoku-solved');
            }
        });
    }

    // Imprimir tablero en consola
    function printBoardToConsole(board, title) {
        console.log(`\n${title}:`);
        console.log("+-------+-------+-------+");

        for (let i = 0; i < 9; i++) {
            let row = "| ";
            for (let j = 0; j < 9; j++) {
                row += (board[i][j] === 0 ? "." : board[i][j]) + " ";
                if ((j + 1) % 3 === 0) {
                    row += "| ";
                }
            }
            console.log(row);

            if ((i + 1) % 3 === 0 && i < 8) {
                console.log("+-------+-------+-------+");
            }
        }

        console.log("+-------+-------+-------+");
    }

    // Crear vista previa del tablero
    function createPreview(grid, isOriginal = false) {
        const container = document.createElement('div');
        container.className = 'sudoku-solver-grid';

        for (let i = 0; i < 9; i++) {
            for (let j = 0; j < 9; j++) {
                const cell = document.createElement('div');
                cell.className = 'sudoku-solver-cell';

                if (isOriginal && grid[i][j] !== 0) {
                    cell.classList.add('original');
                } else if (!isOriginal && grid[i][j] !== 0) {
                    cell.classList.add('solved');
                }

                cell.textContent = grid[i][j] === 0 ? '' : grid[i][j];
                container.appendChild(cell);
            }
        }

        return container;
    }

    // ==============================================
    // INTERFAZ DE USUARIO
    // ==============================================

    function createUI() {
        // Crear panel principal
        const panel = document.createElement('div');
        panel.className = 'sudoku-solver-panel';
        panel.innerHTML = `
            <div class="sudoku-solver-title">Solucionador de Sudoku</div>

            <div id="sudokuStatus" class="sudoku-solver-status sudoku-solver-info">
                Listo para resolver. Primero haz clic en "Extraer Sudoku".
            </div>

            <button id="extractBtn" class="sudoku-solver-btn">Extraer Sudoku</button>
            <button id="solveBtn" class="sudoku-solver-btn blue" disabled>Resolver</button>
            <button id="stepBtn" class="sudoku-solver-btn orange" disabled>Paso a Paso</button>
            <button id="restoreBtn" class="sudoku-solver-btn" disabled>Restaurar Original</button>

            <div id="previewArea" style="display: none;">
                <div style="margin: 10px 0 5px 0; font-size: 13px; font-weight: bold;">Vista previa:</div>
                <div id="previewContainer"></div>
                <div id="statsContainer" class="sudoku-solver-stats"></div>
            </div>
        `;

        document.body.appendChild(panel);

        // Referencias a elementos
        const extractBtn = document.getElementById('extractBtn');
        const solveBtn = document.getElementById('solveBtn');
        const stepBtn = document.getElementById('stepBtn');
        const restoreBtn = document.getElementById('restoreBtn');
        const statusDiv = document.getElementById('sudokuStatus');
        const previewArea = document.getElementById('previewArea');
        const previewContainer = document.getElementById('previewContainer');
        const statsContainer = document.getElementById('statsContainer');

        let originalBoard = null;
        let solvedBoard = null;

        // Función para actualizar estadísticas
        function updateStats(stats) {
            if (!stats) {
                statsContainer.innerHTML = '';
                return;
            }

            statsContainer.innerHTML = `
                <strong>Estadísticas:</strong><br>
                Pasos: ${stats.steps.toLocaleString()}<br>
                Tiempo: ${stats.time.toFixed(2)} ms<br>
                Profundidad máxima: ${stats.maxDepth}
            `;
        }

        // Función para actualizar estado
        function updateStatus(message, type = 'info') {
            statusDiv.textContent = message;
            statusDiv.className = `sudoku-solver-status sudoku-solver-${type}`;
        }

        // Extraer sudoku de la página
        extractBtn.addEventListener('click', function() {
            try {
                updateStatus("Extrayendo sudoku de la página...", "info");

                originalBoard = extractSudoku();
                printBoardToConsole(originalBoard, "Sudoku Original");

                // Mostrar vista previa
                previewContainer.innerHTML = '';
                previewContainer.appendChild(createPreview(originalBoard, true));
                previewArea.style.display = 'block';

                // Habilitar botones
                solveBtn.disabled = false;
                stepBtn.disabled = false;

                updateStatus("Sudoku extraído correctamente. Ahora puedes resolverlo.", "success");

            } catch (error) {
                console.error("Error al extraer sudoku:", error);
                updateStatus(`Error: ${error.message}`, "error");
            }
        });

        // Resolver sudoku
        solveBtn.addEventListener('click', function() {
            if (!originalBoard) {
                updateStatus("Primero extrae el sudoku.", "error");
                return;
            }

            solveBtn.disabled = true;
            stepBtn.disabled = true;
            extractBtn.disabled = true;
            solveBtn.textContent = "Resolviendo...";

            updateStatus("Resolviendo sudoku con backtracking...", "info");

            // Resolver en un setTimeout para no bloquear la UI
            setTimeout(() => {
                try {
                    const solver = new SudokuSolver();
                    const result = solver.solve(originalBoard);

                    if (result.solved) {
                        solvedBoard = result.solution;

                        printBoardToConsole(solvedBoard, "Sudoku Resuelto");

                        // Mostrar solución en la página
                        displaySolution(originalBoard, solvedBoard);

                        // Actualizar vista previa
                        previewContainer.innerHTML = '';
                        previewContainer.appendChild(createPreview(solvedBoard));

                        // Mostrar estadísticas
                        updateStats(result);

                        updateStatus(`¡Sudoku resuelto! ${result.steps} pasos en ${result.time.toFixed(2)} ms`, "success");

                        // Habilitar botón de restaurar
                        restoreBtn.disabled = false;

                        console.log("Sudoku resuelto exitosamente.");
                    } else {
                        updateStatus("No se pudo resolver el sudoku. Puede que no tenga solución.", "error");
                    }
                } catch (error) {
                    console.error("Error al resolver:", error);
                    updateStatus(`Error: ${error.message}`, "error");
                } finally {
                    solveBtn.disabled = false;
                    stepBtn.disabled = false;
                    extractBtn.disabled = false;
                    solveBtn.textContent = "Resolver";
                }
            }, 10);
        });

        // Resolver paso a paso
        stepBtn.addEventListener('click', async function() {
            if (!originalBoard) {
                updateStatus("Primero extrae el sudoku.", "error");
                return;
            }

            solveBtn.disabled = true;
            stepBtn.disabled = true;
            extractBtn.disabled = true;
            stepBtn.textContent = "Resolviendo...";

            updateStatus("Resolviendo paso a paso (puede tomar unos segundos)...", "info");

            try {
                const solver = new SudokuSolver();
                let stepCount = 0;

                const result = await solver.solveStepByStep(originalBoard, async (board, steps) => {
                    stepCount = steps;

                    // Actualizar vista previa cada 200 pasos
                    if (steps % 200 === 0) {
                        previewContainer.innerHTML = '';
                        previewContainer.appendChild(createPreview(board));
                        updateStatus(`Resolviendo... ${steps} pasos`, "info");

                        // Pequeña pausa para visualización
                        await new Promise(resolve => setTimeout(resolve, 10));
                    }
                });

                if (result.solved) {
                    solvedBoard = result.solution;

                    // Mostrar solución final en la página
                    displaySolution(originalBoard, solvedBoard);

                    // Mostrar vista previa final
                    previewContainer.innerHTML = '';
                    previewContainer.appendChild(createPreview(solvedBoard));

                    // Mostrar estadísticas
                    updateStats(result);

                    updateStatus(`¡Sudoku resuelto paso a paso! ${result.steps} pasos en ${result.time.toFixed(2)} ms`, "success");

                    // Habilitar botón de restaurar
                    restoreBtn.disabled = false;
                } else {
                    updateStatus("No se pudo resolver el sudoku.", "error");
                }
            } catch (error) {
                console.error("Error:", error);
                updateStatus(`Error: ${error.message}`, "error");
            } finally {
                solveBtn.disabled = false;
                stepBtn.disabled = false;
                extractBtn.disabled = false;
                stepBtn.textContent = "Paso a Paso";
            }
        });

        // Restaurar original
        restoreBtn.addEventListener('click', function() {
            if (originalBoard) {
                restoreOriginal(originalBoard);
                previewContainer.innerHTML = '';
                previewContainer.appendChild(createPreview(originalBoard, true));
                updateStats(null);
                updateStatus("Sudoku restaurado a su estado original.", "info");
            }
        });
    }

    // ==============================================
    // INICIALIZACIÓN
    // ==============================================

    function init() {
        // Esperar a que la página cargue
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', createUI);
        } else {
            // Si ya está cargada, crear la UI directamente
            setTimeout(createUI, 1000);
        }

        // También escuchar cambios en la URL (por si cambian de sudoku)
        let lastUrl = location.href;
        new MutationObserver(() => {
            const url = location.href;
            if (url !== lastUrl) {
                lastUrl = url;
                // Si ya existe el panel, eliminarlo y recrearlo
                const existingPanel = document.querySelector('.sudoku-solver-panel');
                if (existingPanel) {
                    existingPanel.remove();
                    setTimeout(createUI, 500);
                }
            }
        }).observe(document, {subtree: true, childList: true});
    }

    // Iniciar
    init();
})();