
    // Initialize the board (7x7 grid)
    window.board = Array(7).fill().map(() => Array(7).fill('_'));

    export function checkWinner(board) {
        for (let row = 0; row < 7; row++) {
            for (let col = 0; col < 7; col++) {
                let player = board[row][col];
                if (player === '_') continue; // Skip empty cells

                let count = 1;
                for (let i = 1; col + i < 7 && board[row][col + i] === player; i++) count++; // Right
                for (let i = 1; col - i >= 0 && board[row][col - i] === player; i++) count++; // Left
                if (count >= 4) return player;

                count = 1;
                for (let i = 1; row + i < 7 && board[row + i][col] === player; i++) count++; // Down
                for (let i = 1; row - i >= 0 && board[row - i][col] === player; i++) count++; // Up
                if (count >= 4) return player;

                count = 1;
                for (let i = 1; row + i < 7 && col + i < 7 && board[row + i][col + i] === player; i++) count++; // Down-Right
                for (let i = 1; row - i >= 0 && col - i >= 0 && board[row - i][col - i] === player; i++) count++; // Up-Left
                if (count >= 4) return player;

                count = 1;
                for (let i = 1; row - i >= 0 && col + i < 7 && board[row - i][col + i] === player; i++) count++; // Up-Right
                for (let i = 1; row + i < 7 && col - i >= 0 && board[row + i][col - i] === player; i++) count++; // Down-Left
                if (count >= 4) return player;
            }
        }

        return null; // No winner found
    }
