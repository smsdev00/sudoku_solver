// ==UserScript==
// @name         Solucionador de Sudoku con Backtracking y API
// @namespace    http://tampermonkey.net/
// @version      5.1
// @description  Extrae y resuelve sudokus usando backtracking local o API externa con animación opcional
// @author       Asistente de Código
// @match *://*.sudoku-online.org/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=sudoku-online.org
// @grant        GM_addStyle
// @grant        GM_xmlhttpRequest
// ==/UserScript==

(function() {
    'use strict';

    // Agregar estilos CSS (se mantienen iguales)
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
            width: 520px;
            font-family: Arial, sans-serif;
            max-height: 95vh;
            overflow-y: auto;
        }

        .sudoku-solver-title {
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
            border-bottom: 1px solid #eee;
            padding-bottom: 8px;
            font-size: 16px;
            text-align: center;
        }

        .sudoku-solver-btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            margin: 5px;
            font-size: 14px;
            transition: background 0.3s;
            flex: 1;
            min-width: 120px;
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

        .sudoku-solver-btn.purple {
            background: #9C27B0;
        }

        .sudoku-solver-btn.purple:hover {
            background: #7B1FA2;
        }

        .sudoku-solver-btn.red {
            background: #F44336;
        }

        .sudoku-solver-btn.red:hover {
            background: #D32F2F;
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

        .sudoku-solver-auto-controls,
        .sudoku-solver-animation-controls,
        .sudoku-solver-api-controls {
            margin: 10px 0;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 4px;
            border: 1px solid #eee;
        }

        .sudoku-solver-input-group {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
            justify-content: space-between;
        }

        .sudoku-solver-input-group label {
            font-size: 13px;
            color: #666;
            flex: 1;
            margin-right: 10px;
        }

        .sudoku-solver-input-group input[type="number"],
        .sudoku-solver-input-group input[type="text"],
        .sudoku-solver-input-group input[type="checkbox"] {
            width: 60px;
            padding: 4px 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            text-align: center;
        }

        .sudoku-solver-input-group input[type="checkbox"] {
            width: auto;
        }

        .sudoku-solver-input-group input[type="text"] {
            width: 200px;
        }

        .sudoku-solver-auto-stats {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
            padding: 5px;
            background-color: #f0f0f0;
            border-radius: 3px;
        }

        .sudoku-solver-animation-option {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
            justify-content: space-between;
        }

        .sudoku-solver-animation-option label {
            font-size: 13px;
            color: #333;
            flex: 1;
        }

        .sudoku-solver-cell.animating {
            animation: fill-cell 0.5s ease-in-out;
        }
        
        @keyframes fill-cell {
            0% { transform: scale(0.8); opacity: 0.5; background-color: #e8f5e9; }
            100% { transform: scale(1); opacity: 1; }
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        .blink {
            animation: blink-animation 1s infinite;
        }

        @keyframes blink-animation {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }

        /* Nuevos estilos para dos columnas */
        .sudoku-solver-buttons-row {
            display: flex;
            flex-wrap: wrap;
            margin: 10px 0;
            gap: 5px;
        }

        .sudoku-solver-buttons-row .sudoku-solver-btn {
            flex: 1 1 calc(50% - 10px);
            margin: 5px;
        }

        .sudoku-solver-controls-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin: 10px 0;
        }

        .sudoku-solver-section {
            margin-bottom: 15px;
        }

        .sudoku-solver-section-title {
            font-size: 14px;
            font-weight: bold;
            color: #333;
            margin-bottom: 8px;
            padding-bottom: 5px;
            border-bottom: 1px solid #eee;
        }

        .sudoku-solver-preview-section {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }

        /* Radio button styles */
        .sudoku-solver-radio-group {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
            gap: 15px;
        }

        .sudoku-solver-radio-group label {
            display: flex;
            align-items: center;
            font-size: 13px;
            color: #666;
            cursor: pointer;
        }

        .sudoku-solver-radio-group input[type="radio"] {
            margin-right: 5px;
            cursor: pointer;
        }

        /* Combinaciones info */
        .sudoku-solver-combinations {
            font-size: 12px;
            color: #333;
            margin-bottom: 10px;
            padding: 8px;
            background-color: #f0f8ff;
            border-radius: 4px;
            border-left: 4px solid #2196F3;
        }

        .sudoku-solver-combinations .label {
            font-weight: bold;
            color: #1976D2;
        }

        .sudoku-solver-combinations .value {
            font-weight: bold;
            color: #4CAF50;
        }

        .sudoku-solver-combinations .note {
            font-size: 11px;
            color: #666;
            margin-top: 3px;
            font-style: italic;
        }

        /* Scrollbar personalizada */
        .sudoku-solver-panel::-webkit-scrollbar {
            width: 8px;
        }

        .sudoku-solver-panel::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }

        .sudoku-solver-panel::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 4px;
        }

        .sudoku-solver-panel::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
    `);

    // ==============================================
    // ALGORITMO DE BACKTRACKING LOCAL
    // ==============================================

    class SudokuSolver {
        constructor() {
            this.steps = 0;
            this.startTime = 0;
            this.maxDepth = 0;
        }

        nextEmptySpot(board) {
            for (let i = 0; i < 9; i++) {
                for (let j = 0; j < 9; j++) {
                    if (board[i][j] === 0) {
                        return [i, j];
                    }
                }
            }
            return [-1, -1];
        }

        checkRow(board, row, value) {
            for (let i = 0; i < 9; i++) {
                if (board[row][i] === value) {
                    return false;
                }
            }
            return true;
        }

        checkColumn(board, column, value) {
            for (let i = 0; i < 9; i++) {
                if (board[i][column] === value) {
                    return false;
                }
            }
            return true;
        }

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

        checkValue(board, row, column, value) {
            return this.checkRow(board, row, value) &&
                   this.checkColumn(board, column, value) &&
                   this.checkSquare(board, row, column, value);
        }

        solve(board) {
            this.steps = 0;
            this.startTime = performance.now();

            const solveRecursive = (board) => {
                this.steps++;

                let emptySpot = this.nextEmptySpot(board);
                let row = emptySpot[0];
                let col = emptySpot[1];

                if (row === -1) {
                    return true;
                }

                for (let num = 1; num <= 9; num++) {
                    if (this.checkValue(board, row, col, num)) {
                        board[row][col] = num;

                        const filled = this.countFilledCells(board);
                        this.maxDepth = Math.max(this.maxDepth, filled);

                        if (solveRecursive(board)) {
                            return true;
                        }

                        board[row][col] = 0;
                    }
                }

                return false;
            };

            const boardCopy = JSON.parse(JSON.stringify(board));
            const solved = solveRecursive(boardCopy);

            const endTime = performance.now();

            return {
                solved: solved,
                solution: solved ? boardCopy : null,
                steps: this.steps,
                time: endTime - this.startTime,
                maxDepth: this.maxDepth,
                method: "backtracking_local"
            };
        }

        async solveStepByStep(board, callback = null) {
            this.steps = 0;
            this.startTime = performance.now();
            this.maxDepth = 0;

            const boardCopy = JSON.parse(JSON.stringify(board));

            const solveRecursiveStep = async (board) => {
                this.steps++;

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
                maxDepth: this.maxDepth,
                method: "backtracking_local"
            };
        }

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

        countSolutions(board, maxSolutions = 100) {
            this.steps = 0;
            this.startTime = performance.now();
            let solutionCount = 0;
            const solutions = [];

            const solveRecursiveCount = (board) => {
                this.steps++;

                // Límite de tiempo y soluciones
                if (performance.now() - this.startTime > 1000) { // 1 segundo máximo
                    return false;
                }

                if (solutionCount >= maxSolutions) {
                    return false;
                }

                let emptySpot = this.nextEmptySpot(board);
                let row = emptySpot[0];
                let col = emptySpot[1];

                if (row === -1) {
                    solutions.push(JSON.parse(JSON.stringify(board)));
                    solutionCount++;
                    return true;
                }

                for (let num = 1; num <= 9 && solutionCount < maxSolutions; num++) {
                    if (this.checkValue(board, row, col, num)) {
                        board[row][col] = num;

                        solveRecursiveCount(board);

                        board[row][col] = 0;
                    }
                }

                return false;
            };

            const boardCopy = JSON.parse(JSON.stringify(board));
            solveRecursiveCount(boardCopy);

            const endTime = performance.now();

            return {
                count: solutionCount,
                estimatedTotal: this.estimateTotalSolutions(board, solutionCount),
                steps: this.steps,
                time: endTime - this.startTime,
                limited: solutionCount >= maxSolutions,
                timeout: (endTime - this.startTime) >= 1000
            };
        }

        estimateTotalSolutions(board, foundSolutions) {
            const emptyCells = 81 - this.countFilledCells(board);
            
            if (emptyCells <= 20) {
                // Para tableros con pocas celdas vacías, podemos estimar mejor
                return foundSolutions;
            } else if (emptyCells <= 40) {
                // Estimación simple basada en celdas vacías
                return Math.min(foundSolutions * 10, 1000000);
            } else {
                // Demasiadas celdas vacías para estimar
                return "más de " + (foundSolutions * 100);
            }
        }
    }

    // ==============================================
    // FUNCIÓN PARA USAR LA API
    // ==============================================

    async function solveWithAPI(grid, apiUrl) {
        const startTime = performance.now();
        
        return new Promise((resolve, reject) => {
            GM_xmlhttpRequest({
                method: 'POST',
                url: `${apiUrl}/solve`,
                headers: {
                    'Content-Type': 'application/json'
                },
                data: JSON.stringify({ grid: grid }),
                responseType: 'json',
                timeout: 30000,
                onload: function(response) {
                    const endTime = performance.now();
                    
                    if (response.status === 200) {
                        const data = response.response;
                        resolve({
                            solved: data.solved,
                            solution: data.solution,
                            steps: data.steps || 0,
                            time: data.time_ms || (endTime - startTime),
                            message: data.message,
                            method: data.method || "api"
                        });
                    } else {
                        reject(new Error(`API error ${response.status}: ${response.response?.detail || 'Unknown error'}`));
                    }
                },
                onerror: function(error) {
                    reject(new Error(`Network error: ${error.statusText || 'Cannot connect to API'}`));
                },
                ontimeout: function() {
                    reject(new Error('API request timeout'));
                }
            });
        });
    }

    // ==============================================
    // FUNCIONES AUXILIARES
    // ==============================================

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    function randomSleep(min, max) {
        return new Promise(resolve => 
            setTimeout(resolve, Math.random() * (max - min) + min)
        );
    }

    function shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    // ==============================================
    // FUNCIONES PARA INTERACTUAR CON LA PÁGINA WEB
    // ==============================================

    function extractSudoku() {
        const sudokuGrid = [];

        for (let i = 0; i < 9; i++) {
            sudokuGrid[i] = Array(9).fill(0);
        }

        const sudokuElements = document.querySelectorAll('[id^="sudo_input_"], div[class*="sudo_field"]');

        if (sudokuElements.length === 0) {
            throw new Error("No se encontraron elementos del sudoku. ¿Estás en la página correcta?");
        }

        sudokuElements.forEach(element => {
            let row, col;

            if (element.hasAttribute('data-x') && element.hasAttribute('data-y')) {
                row = parseInt(element.getAttribute('data-x'));
                col = parseInt(element.getAttribute('data-y'));
            }
            else if (element.id && element.id.startsWith('sudo_input_')) {
                const index = parseInt(element.id.replace('sudo_input_', ''));
                row = Math.floor(index / 9);
                col = index % 9;
            }
            else if (element.hasAttribute('data-index')) {
                const index = parseInt(element.getAttribute('data-index'));
                row = Math.floor(index / 9);
                col = index % 9;
            }

            let value = 0;
            const textContent = element.textContent.trim();
            if (textContent && !isNaN(textContent) && textContent !== '') {
                value = parseInt(textContent, 10);
            }

            if (row !== undefined && col !== undefined && row >= 0 && row < 9 && col >= 0 && col < 9) {
                sudokuGrid[row][col] = value;
            }
        });

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

    function displaySolution(originalGrid, solvedGrid) {
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
                const solvedValue = solvedGrid[row][col];

                if (originalValue === 0 || originalValue !== solvedValue) {
                    element.textContent = solvedValue;
                    element.style.color = '#4CAF50';
                    element.style.fontWeight = 'bold';
                    element.classList.add('sudoku-solved');
                }
            }
        });
    }

    async function displaySolutionWithAnimation(originalGrid, solvedGrid, minDelay = 50, maxDelay = 200) {
        const sudokuElements = document.querySelectorAll('[id^="sudo_input_"], div[class*="sudo_field"]');
        
        const cellsToUpdate = [];
        
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
                const solvedValue = solvedGrid[row][col];

                if (originalValue === 0 || originalValue !== solvedValue) {
                    cellsToUpdate.push({
                        element: element,
                        solvedValue: solvedValue,
                        row: row,
                        col: col
                    });
                }
            }
        });
        
        shuffleArray(cellsToUpdate);
        
        for (const cell of cellsToUpdate) {
            await randomSleep(minDelay, maxDelay);
            
            cell.element.textContent = cell.solvedValue;
            cell.element.style.color = '#4CAF50';
            cell.element.style.fontWeight = 'bold';
            cell.element.classList.add('sudoku-solved', 'animating');
            
            setTimeout(() => {
                cell.element.classList.remove('animating');
            }, 500);
        }
    }

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

    function createCombinationsInfo(board, combinationsData = null) {
        const infoDiv = document.createElement('div');
        infoDiv.className = 'sudoku-solver-combinations';
        
        const filledCells = board.flat().filter(cell => cell !== 0).length;
        const emptyCells = 81 - filledCells;
        
        let infoHTML = `<span class="label">Celdas llenas:</span> <span class="value">${filledCells}/81</span>`;
        infoHTML += ` | <span class="label">Vacías:</span> <span class="value">${emptyCells}</span>`;
        
        if (combinationsData) {
            if (combinationsData.timeout) {
                infoHTML += `<br><span class="label">Combinaciones estimadas:</span> <span class="value">${combinationsData.estimatedTotal}</span>`;
                infoHTML += `<div class="note">(cálculo limitado por tiempo, estimación aproximada)</div>`;
            } else if (combinationsData.limited) {
                infoHTML += `<br><span class="label">Combinaciones encontradas:</span> <span class="value">≥ ${combinationsData.count}</span>`;
                infoHTML += `<div class="note">(mínimo ${combinationsData.count} soluciones únicas encontradas en ${combinationsData.steps} pasos)</div>`;
            } else {
                infoHTML += `<br><span class="label">Combinaciones estimadas:</span> <span class="value">${combinationsData.estimatedTotal}</span>`;
                infoHTML += `<div class="note">(${combinationsData.count} soluciones encontradas en ${combinationsData.steps} pasos, ${combinationsData.time.toFixed(0)} ms)</div>`;
            }
        } else {
            infoHTML += `<div class="note">Haz clic en "Calcular Combinaciones" para estimar soluciones posibles</div>`;
        }
        
        infoDiv.innerHTML = infoHTML;
        return infoDiv;
    }

    // ==============================================
    // INTERFAZ DE USUARIO
    // ==============================================

    function createUI() {
        const panel = document.createElement('div');
        panel.className = 'sudoku-solver-panel';
        panel.innerHTML = `
            <div class="sudoku-solver-title">Solucionador de Sudoku</div>

            <div id="sudokuStatus" class="sudoku-solver-status sudoku-solver-info">
                Listo para resolver. Primero haz clic en "Extraer Sudoku".
            </div>

            <div class="sudoku-solver-section">
                <div class="sudoku-solver-section-title">Controles Principales</div>
                <div class="sudoku-solver-buttons-row">
                    <button id="extractBtn" class="sudoku-solver-btn">Extraer Sudoku</button>
                    <button id="solveBtn" class="sudoku-solver-btn blue" disabled>Resolver</button>
                    <button id="stepBtn" class="sudoku-solver-btn orange" disabled>Paso a Paso</button>
                    <button id="restoreBtn" class="sudoku-solver-btn" disabled>Restaurar</button>
                    <button id="newBtn" class="sudoku-solver-btn">Nuevo</button>
                    <button id="calcCombinationsBtn" class="sudoku-solver-btn" disabled>Calcular Combinaciones</button>
                </div>
            </div>

            <div class="sudoku-solver-section">
                <div class="sudoku-solver-section-title">Método de Resolución</div>
                <div class="sudoku-solver-radio-group">
                    <label>
                        <input type="radio" name="solverMethod" value="local" checked> Local (Backtracking)
                    </label>
                    <label>
                        <input type="radio" name="solverMethod" value="api"> API Externa
                    </label>
                </div>
            </div>

            <div class="sudoku-solver-controls-grid">
                <div class="sudoku-solver-section">
                    <div class="sudoku-solver-section-title">Animación</div>
                    <div class="sudoku-solver-animation-controls">
                        <div class="sudoku-solver-animation-option">
                            <label for="animationCheckbox">Usar animación:</label>
                            <input type="checkbox" id="animationCheckbox" checked>
                        </div>
                        <div id="animationSettings">
                            <div class="sudoku-solver-input-group">
                                <label for="animMinDelay">Mín (ms):</label>
                                <input type="number" id="animMinDelay" min="0" max="1000" value="50">
                            </div>
                            <div class="sudoku-solver-input-group">
                                <label for="animMaxDelay">Máx (ms):</label>
                                <input type="number" id="animMaxDelay" min="0" max="2000" value="200">
                            </div>
                        </div>
                    </div>
                </div>

                <div class="sudoku-solver-section">
                    <div class="sudoku-solver-section-title">Configuración API</div>
                    <div class="sudoku-solver-api-controls">
                        <div class="sudoku-solver-input-group">
                            <label for="apiUrl">URL API:</label>
                            <input type="text" id="apiUrl" value="http://127.0.0.1:8888">
                        </div>
                        <div class="sudoku-solver-input-group">
                            <label for="apiTimeout">Timeout (ms):</label>
                            <input type="number" id="apiTimeout" min="1000" max="60000" value="30000">
                        </div>
                    </div>
                </div>
            </div>

            <div class="sudoku-solver-section">
                <div class="sudoku-solver-section-title">Automático</div>
                <div class="sudoku-solver-auto-controls">
                    <div class="sudoku-solver-input-group">
                        <label for="autoCount">Repeticiones:</label>
                        <input type="number" id="autoCount" min="1" max="1000" value="100">
                    </div>
                    <div class="sudoku-solver-input-group">
                        <label for="autoDelay">Delay (ms):</label>
                        <input type="number" id="autoDelay" min="100" max="10000" value="3000">
                    </div>
                    <div class="sudoku-solver-input-group">
                        <label for="autoAnimation">Usar animación:</label>
                        <input type="checkbox" id="autoAnimation">
                    </div>
                    <div class="sudoku-solver-buttons-row">
                        <button id="autoBtn" class="sudoku-solver-btn purple">Auto</button>
                        <button id="stopBtn" class="sudoku-solver-btn red" disabled>Detener</button>
                    </div>
                    <div id="autoStats" class="sudoku-solver-auto-stats"></div>
                </div>
            </div>

            <div class="sudoku-solver-preview-section">
                <div id="previewArea" style="display: none;">
                    <div class="sudoku-solver-section-title">Vista Previa</div>
                    <div id="combinationsInfo"></div>
                    <div id="previewContainer"></div>
                    <div id="statsContainer" class="sudoku-solver-stats"></div>
                </div>
            </div>
        `;

        document.body.appendChild(panel);

        const extractBtn = document.getElementById('extractBtn');
        const solveBtn = document.getElementById('solveBtn');
        const stepBtn = document.getElementById('stepBtn');
        const restoreBtn = document.getElementById('restoreBtn');
        const newBtn = document.getElementById('newBtn');
        const calcCombinationsBtn = document.getElementById('calcCombinationsBtn');
        const autoBtn = document.getElementById('autoBtn');
        const stopBtn = document.getElementById('stopBtn');
        const animationCheckbox = document.getElementById('animationCheckbox');
        const animationSettings = document.getElementById('animationSettings');
        const autoAnimationCheckbox = document.getElementById('autoAnimation');
        const autoCountInput = document.getElementById('autoCount');
        const autoDelayInput = document.getElementById('autoDelay');
        const animMinDelayInput = document.getElementById('animMinDelay');
        const animMaxDelayInput = document.getElementById('animMaxDelay');
        const apiUrlInput = document.getElementById('apiUrl');
        const apiTimeoutInput = document.getElementById('apiTimeout');
        const statusDiv = document.getElementById('sudokuStatus');
        const previewArea = document.getElementById('previewArea');
        const previewContainer = document.getElementById('previewContainer');
        const statsContainer = document.getElementById('statsContainer');
        const combinationsInfo = document.getElementById('combinationsInfo');
        const autoStatsDiv = document.getElementById('autoStats');
        const solverMethodRadios = document.querySelectorAll('input[name="solverMethod"]');

        let originalBoard = null;
        let solvedBoard = null;
        let autoModeActive = false;
        let currentIteration = 0;
        let totalIterations = 0;
        let totalSolved = 0;
        let totalErrors = 0;
        let totalTime = 0;
        let currentCombinationsData = null;

        // Mostrar/ocultar configuración de animación
        animationCheckbox.addEventListener('change', function() {
            animationSettings.style.display = this.checked ? 'block' : 'none';
        });

        // Inicializar visibilidad de animación
        animationSettings.style.display = animationCheckbox.checked ? 'block' : 'none';

        // Actualizar visibilidad de controles según método seleccionado
        function updateControlsVisibility() {
            const useAPI = document.querySelector('input[name="solverMethod"]:checked').value === 'api';
            
            // Deshabilitar paso a paso si se usa API
            stepBtn.disabled = useAPI || originalBoard === null;
            
            // Mostrar/ocultar configuración de API
            document.querySelector('.sudoku-solver-api-controls').style.display = useAPI ? 'block' : 'none';
            
            // Animación siempre disponible, incluso con API
            animationCheckbox.disabled = false;
        }

        // Inicializar visibilidad de controles
        updateControlsVisibility();

        // Escuchar cambios en el método de resolución
        solverMethodRadios.forEach(radio => {
            radio.addEventListener('change', updateControlsVisibility);
        });

        function updateAutoStats() {
            autoStatsDiv.innerHTML = `
                <strong>Estadísticas Auto:</strong><br>
                Iteración: ${currentIteration}/${totalIterations}<br>
                Resueltos: ${totalSolved}<br>
                Errores: ${totalErrors}<br>
                Tiempo total: ${totalTime.toFixed(2)} ms
            `;
        }

        function updateStats(stats) {
            if (!stats) {
                statsContainer.innerHTML = '';
                return;
            }

            statsContainer.innerHTML = `
                <strong>Estadísticas:</strong><br>
                Método: ${stats.method || 'Local'}<br>
                Pasos: ${stats.steps.toLocaleString()}<br>
                Tiempo: ${stats.time.toFixed(2)} ms<br>
                ${stats.maxDepth ? `Profundidad máxima: ${stats.maxDepth}` : ''}
            `;
        }

        function updateStatus(message, type = 'info') {
            statusDiv.textContent = message;
            statusDiv.className = `sudoku-solver-status sudoku-solver-${type}`;
        }

        function updatePreview(board, isOriginal = true, combinationsData = null) {
            previewContainer.innerHTML = '';
            previewContainer.appendChild(createPreview(board, isOriginal));
            
            combinationsInfo.innerHTML = '';
            combinationsInfo.appendChild(createCombinationsInfo(board, combinationsData));
        }

        async function calculateCombinations() {
            if (!originalBoard) {
                updateStatus("Primero extrae el sudoku.", "error");
                return;
            }

            calcCombinationsBtn.disabled = true;
            calcCombinationsBtn.textContent = "Calculando...";
            
            updateStatus("Calculando combinaciones posibles... (máximo 1 segundo)", "info");
            
            setTimeout(async () => {
                try {
                    const solver = new SudokuSolver();
                    currentCombinationsData = solver.countSolutions(originalBoard, 100);
                    
                    updatePreview(originalBoard, true, currentCombinationsData);
                    
                    if (currentCombinationsData.timeout) {
                        updateStatus("Cálculo de combinaciones interrumpido por tiempo. Resultado estimado.", "warning");
                    } else {
                        updateStatus(`Combinaciones calculadas: ${currentCombinationsData.estimatedTotal} estimadas`, "success");
                    }
                } catch (error) {
                    console.error("Error al calcular combinaciones:", error);
                    updateStatus(`Error: ${error.message}`, "error");
                } finally {
                    calcCombinationsBtn.disabled = false;
                    calcCombinationsBtn.textContent = "Calcular Combinaciones";
                }
            }, 10);
        }

        async function startAutoMode() {
            if (autoModeActive) return;
            
            const useAPI = document.querySelector('input[name="solverMethod"]:checked').value === 'api';
            
            totalIterations = parseInt(autoCountInput.value) || 100;
            const delay = parseInt(autoDelayInput.value) || 3000;
            const useAnimation = autoAnimationCheckbox.checked;
            const animMinDelay = parseInt(animMinDelayInput.value) || 50;
            const animMaxDelay = parseInt(animMaxDelayInput.value) || 200;
            
            if (totalIterations < 1) {
                updateStatus("El número de repeticiones debe ser al menos 1.", "error");
                return;
            }
            
            autoModeActive = true;
            currentIteration = 0;
            totalSolved = 0;
            totalErrors = 0;
            totalTime = 0;
            
            extractBtn.disabled = true;
            solveBtn.disabled = true;
            stepBtn.disabled = true;
            restoreBtn.disabled = true;
            newBtn.disabled = true;
            calcCombinationsBtn.disabled = true;
            autoBtn.disabled = true;
            stopBtn.disabled = false;
            autoCountInput.disabled = true;
            autoDelayInput.disabled = true;
            autoAnimationCheckbox.disabled = true;
            
            autoBtn.textContent = "Ejecutando...";
            autoBtn.classList.add('blink');
            
            updateStatus(`Iniciando modo automático para ${totalIterations} sudokus...`, "info");
            
            for (currentIteration = 1; currentIteration <= totalIterations; currentIteration++) {
                if (!autoModeActive) break;
                
                updateStatus(`[${currentIteration}/${totalIterations}] Procesando sudoku...`, "info");
                updateAutoStats();
                
                try {
                    originalBoard = extractSudoku();
                    
                    // Actualizar vista previa para el juego actual
                    updatePreview(originalBoard, true);
                    
                    let result;
                    
                    if (useAPI) {
                        const apiUrl = apiUrlInput.value;
                        result = await solveWithAPI(originalBoard, apiUrl);
                    } else {
                        const solver = new SudokuSolver();
                        result = solver.solve(originalBoard);
                    }
                    
                    if (result.solved) {
                        solvedBoard = result.solution;
                        
                        if (useAnimation) {
                            await displaySolutionWithAnimation(originalBoard, solvedBoard, animMinDelay, animMaxDelay);
                        } else {
                            displaySolution(originalBoard, solvedBoard);
                        }
                        
                        // Actualizar vista previa con solución
                        updatePreview(solvedBoard, false);
                        
                        totalSolved++;
                        totalTime += result.time;
                        
                        updateStatus(`[${currentIteration}/${totalIterations}] ¡Resuelto! ${result.steps} pasos en ${result.time.toFixed(2)} ms (${result.method})`, "success");
                    } else {
                        totalErrors++;
                        updateStatus(`[${currentIteration}/${totalIterations}] Error: No se pudo resolver`, "error");
                    }
                    
                    updateAutoStats();
                    
                    if (currentIteration < totalIterations && autoModeActive) {
                        updateStatus(`[${currentIteration}/${totalIterations}] Esperando ${delay/1000} segundos antes del siguiente...`, "info");
                        await sleep(delay);
                    }
                    
                    if (currentIteration < totalIterations && autoModeActive) {
                        if (typeof sudo_nuevo === 'function') {
                            sudo_nuevo();
                            await sleep(1000);
                        } else {
                            updateStatus("Función 'sudo_nuevo' no encontrada", "error");
                            stopAutoMode();
                            break;
                        }
                    }
                    
                } catch (error) {
                    totalErrors++;
                    console.error(`Error en iteración ${currentIteration}:`, error);
                    updateStatus(`[${currentIteration}/${totalIterations}] Error: ${error.message}`, "error");
                    
                    if (currentIteration < totalIterations && autoModeActive) {
                        await sleep(2000);
                        if (typeof sudo_nuevo === 'function') {
                            sudo_nuevo();
                            await sleep(1000);
                        }
                    }
                }
            }
            
            stopAutoMode();
            
            if (autoModeActive) {
                updateStatus(`Modo automático completado: ${totalSolved}/${totalIterations} resueltos, ${totalErrors} errores`, "success");
            } else {
                updateStatus(`Modo automático detenido: ${totalSolved}/${currentIteration-1} resueltos, ${totalErrors} errores`, "info");
            }
        }
        
        function stopAutoMode() {
            autoModeActive = false;
            
            extractBtn.disabled = false;
            solveBtn.disabled = originalBoard === null;
            stepBtn.disabled = originalBoard === null || document.querySelector('input[name="solverMethod"]:checked').value === 'api';
            restoreBtn.disabled = originalBoard === null || solvedBoard === null;
            newBtn.disabled = false;
            calcCombinationsBtn.disabled = originalBoard === null;
            autoBtn.disabled = false;
            stopBtn.disabled = true;
            autoCountInput.disabled = false;
            autoDelayInput.disabled = false;
            autoAnimationCheckbox.disabled = false;
            
            autoBtn.textContent = "Auto";
            autoBtn.classList.remove('blink');
            
            updateAutoStats();
        }

        extractBtn.addEventListener('click', function() {
            try {
                updateStatus("Extrayendo sudoku de la página...", "info");

                originalBoard = extractSudoku();
                printBoardToConsole(originalBoard, "Sudoku Original");

                previewArea.style.display = 'block';
                updatePreview(originalBoard, true);

                solveBtn.disabled = false;
                stepBtn.disabled = document.querySelector('input[name="solverMethod"]:checked').value === 'api';
                calcCombinationsBtn.disabled = false;

                updateStatus("Sudoku extraído correctamente. Ahora puedes resolverlo.", "success");

            } catch (error) {
                console.error("Error al extraer sudoku:", error);
                updateStatus(`Error: ${error.message}`, "error");
            }
        });

        solveBtn.addEventListener('click', async function() {
            if (!originalBoard) {
                updateStatus("Primero extrae el sudoku.", "error");
                return;
            }

            const useAPI = document.querySelector('input[name="solverMethod"]:checked').value === 'api';
            
            solveBtn.disabled = true;
            stepBtn.disabled = true;
            extractBtn.disabled = true;
            calcCombinationsBtn.disabled = true;
            solveBtn.textContent = "Resolviendo...";

            updateStatus(useAPI ? "Enviando a la API..." : "Resolviendo sudoku con backtracking...", "info");

            setTimeout(async () => {
                try {
                    let result;
                    
                    if (useAPI) {
                        const apiUrl = apiUrlInput.value;
                        result = await solveWithAPI(originalBoard, apiUrl);
                    } else {
                        const solver = new SudokuSolver();
                        result = solver.solve(originalBoard);
                    }

                    if (result.solved) {
                        solvedBoard = result.solution;

                        printBoardToConsole(solvedBoard, "Sudoku Resuelto");

                        if (animationCheckbox.checked) {
                            const animMinDelay = parseInt(animMinDelayInput.value) || 50;
                            const animMaxDelay = parseInt(animMaxDelayInput.value) || 200;
                            await displaySolutionWithAnimation(originalBoard, solvedBoard, animMinDelay, animMaxDelay);
                        } else {
                            displaySolution(originalBoard, solvedBoard);
                        }

                        updatePreview(solvedBoard, false);
                        updateStats(result);

                        updateStatus(`¡Sudoku resuelto! ${result.steps} pasos en ${result.time.toFixed(2)} ms (${result.method})`, "success");

                        restoreBtn.disabled = false;

                        console.log("Sudoku resuelto exitosamente.");
                    } else {
                        updateStatus(`No se pudo resolver el sudoku. ${result.message || ''}`, "error");
                    }
                } catch (error) {
                    console.error("Error al resolver:", error);
                    updateStatus(`Error: ${error.message}`, "error");
                    
                    // Si falla la API, sugerir usar método local
                    if (useAPI) {
                        updateStatus("¿Quieres intentar con el método local?", "info");
                    }
                } finally {
                    solveBtn.disabled = false;
                    stepBtn.disabled = useAPI || originalBoard === null;
                    extractBtn.disabled = false;
                    calcCombinationsBtn.disabled = false;
                    solveBtn.textContent = "Resolver";
                }
            }, 10);
        });

        stepBtn.addEventListener('click', async function() {
            if (!originalBoard) {
                updateStatus("Primero extrae el sudoku.", "error");
                return;
            }

            // Paso a paso solo funciona con método local
            if (document.querySelector('input[name="solverMethod"]:checked').value === 'api') {
                updateStatus("El modo paso a paso solo está disponible con el método local.", "error");
                return;
            }

            solveBtn.disabled = true;
            stepBtn.disabled = true;
            extractBtn.disabled = true;
            calcCombinationsBtn.disabled = true;
            stepBtn.textContent = "Resolviendo...";

            updateStatus("Resolviendo paso a paso (puede tomar unos segundos)...", "info");

            try {
                const solver = new SudokuSolver();
                let stepCount = 0;

                const result = await solver.solveStepByStep(originalBoard, async (board, steps) => {
                    stepCount = steps;

                    if (steps % 200 === 0) {
                        updatePreview(board, false);
                        updateStatus(`Resolviendo... ${steps} pasos`, "info");

                        await new Promise(resolve => setTimeout(resolve, 10));
                    }
                });

                if (result.solved) {
                    solvedBoard = result.solution;

                    if (animationCheckbox.checked) {
                        const animMinDelay = parseInt(animMinDelayInput.value) || 50;
                        const animMaxDelay = parseInt(animMaxDelayInput.value) || 200;
                        await displaySolutionWithAnimation(originalBoard, solvedBoard, animMinDelay, animMaxDelay);
                    } else {
                        displaySolution(originalBoard, solvedBoard);
                    }

                    updatePreview(solvedBoard, false);
                    updateStats(result);

                    updateStatus(`¡Sudoku resuelto paso a paso! ${result.steps} pasos en ${result.time.toFixed(2)} ms`, "success");

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
                calcCombinationsBtn.disabled = false;
                stepBtn.textContent = "Paso a Paso";
            }
        });

        restoreBtn.addEventListener('click', function() {
            if (originalBoard) {
                restoreOriginal(originalBoard);
                updatePreview(originalBoard, true);
                updateStats(null);
                updateStatus("Sudoku restaurado a su estado original.", "info");
            }
        });

        newBtn.addEventListener('click', function() {
            if (typeof sudo_nuevo === 'function') {
                sudo_nuevo();
                updateStatus("Cargando nuevo sudoku...", "info");
            }
        });

        calcCombinationsBtn.addEventListener('click', calculateCombinations);

        autoBtn.addEventListener('click', function() {
            if (!autoModeActive) {
                startAutoMode();
            }
        });

        stopBtn.addEventListener('click', function() {
            stopAutoMode();
            updateStatus("Modo automático detenido por el usuario.", "info");
        });
    }

    // ==============================================
    // INICIALIZACIÓN
    // ==============================================

    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', createUI);
        } else {
            setTimeout(createUI, 1000);
        }

        let lastUrl = location.href;
        new MutationObserver(() => {
            const url = location.href;
            if (url !== lastUrl) {
                lastUrl = url;
                const existingPanel = document.querySelector('.sudoku-solver-panel');
                if (existingPanel) {
                    existingPanel.remove();
                    setTimeout(createUI, 500);
                }
            }
        }).observe(document, {subtree: true, childList: true});
    }

    init();
})();