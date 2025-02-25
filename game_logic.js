    const boardContainer = document.getElementById("board-container");

    // Initialize the board (7x7 grid)
    const board = Array(7).fill().map(() => Array(7).fill('_'));

    export function createBoard() {
    boardContainer.innerHTML = "";
    boardContainer.style.display = "grid";
    boardContainer.style.gridTemplateColumns = "repeat(7, 72px)";
    boardContainer.style.gridGap = "5px";

    for (let row = 0; row < 7; row++) {
        for (let col = 0; col < 7; col++) {
            const cell = document.createElement("div");
            cell.classList.add("cell", "empty");
            cell.dataset.row = row;
            cell.dataset.col = col;
            cell.addEventListener("click", handleCellClick);
            boardContainer.appendChild(cell);
        }
    }
    }


    export function handleCellClick(event) {
    if (gameOver) return;

    const cell = event.target;
    const row = parseInt(cell.dataset.row);
    const col = parseInt(cell.dataset.col);

    if (board[row][col] === '_') {
    if (col === 0 || col === 6 || (col > 0 && board[row][col - 1] !== '_') || (col < 6 && board[row][col + 1] !== '_')) {
        board[row][col] = currentPlayer;
        cell.classList.remove("empty");
        cell.classList.add(currentPlayer);
        cell.textContent = currentPlayer;
        
        if (checkDirection(row, col)) {
            messageDisplay.textContent = `${currentPlayer} wins!`;
            gameOver = true;
            return;
        }
        
        currentPlayer = currentPlayer === 'x' ? 'o' : 'x';
        
        if ((gameMode === 'pvai' && currentPlayer === 'o') || gameMode === 'aivai') {
            aiMove();
        }
    }
    }
    }
