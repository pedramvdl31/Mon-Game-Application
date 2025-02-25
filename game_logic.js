export let currentPlayer = 'x';
export let gameOver = false;
export let gameMode = '';

const boardContainer = document.getElementById("board-container");
const startButton = document.getElementById("start-button");
const gameModeSelect = document.getElementById("game-mode-select");
const messageDisplay = document.getElementById("message");

export const board = Array(7).fill().map(() => Array(7).fill('_'));

export function createBoard() {
    alert()
    boardContainer.innerHTML = "";
    boardContainer.style.display = "grid";
    boardContainer.style.gridTemplateColumns = "repeat(7, 50px)";
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
        }
    }
}

export function checkDirection(row, col) {
    const player = board[row][col];
    
    for (let i = 0; i < 4; i++) {
        if (col + i < 7 && board[row][col + i] === player) {
            if (i === 3) return true;
        } else break;
    }
    
    for (let i = 0; i < 4; i++) {
        if (row + i < 7 && board[row + i][col] === player) {
            if (i === 3) return true;
        } else break;
    }
    
    return false;
}

startButton.addEventListener("click", function () {
    gameMode = gameModeSelect.value;
    boardContainer.style.display = "grid";
    startButton.style.display = "none";
    gameModeSelect.style.display = "none";
    messageDisplay.textContent = "";
    
    board.forEach(row => row.fill('_'));
    createBoard();
    
    currentPlayer = 'x';
    gameOver = false;
});
