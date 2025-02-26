import random
import pickle

# Constants
ROWS = 7
COLS = 7
EMPTY = "_"

# Q-learning parameters
ALPHA = 0.5  # Learning rate
GAMMA = 0.9  # Discount factor

# Function to check for a win
def check_win(board, player):
    for row in range(ROWS):
        for col in range(COLS - 3):
            if all(board[row][col + i] == player for i in range(4)):
                return True

    for col in range(COLS):
        for row in range(ROWS - 3):
            if all(board[row + i][col] == player for i in range(4)):
                return True

    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            if all(board[row + i][col + i] == player for i in range(4)):
                return True

    for row in range(3, ROWS):
        for col in range(COLS - 3):
            if all(board[row - i][col + i] == player for i in range(4)):
                return True
    
    return False

# Function to make a move
def make_move(board, row, player, direction):
    if direction == "left":
        for col in range(len(board[row])):  
            if board[row][col] == EMPTY:  
                board[row][col] = player
                return board, col  
    elif direction == "right":
        for col in range(len(board[row]) - 1, -1, -1):  
            if board[row][col] == EMPTY:
                board[row][col] = player
                return board, col
    print(f"{player} tried to move in row {row}, but found no space.")
    return board, None  

# AI move using Q-learning
def ai_make_move(board, ai_symbol):  # ✅ AI symbol is now passed dynamically
    global Q_TABLE
    state = str(board)

    # ✅ Determine the opponent symbol dynamically
    opponent = "x" if ai_symbol == "o" else "o"

    # 🛑 **Fix: Stop AI if Opponent Has Already Won**
    if check_win(board, opponent):
        print(f"❌ AI ({ai_symbol}) stops: Opponent ({opponent}) has already won.")
        return board  

    # Load Q-table if it exists
    try:
        with open('q_table.pkl', 'rb') as f:
            Q_TABLE = pickle.load(f)
    except FileNotFoundError:
        Q_TABLE = {}

    # Initialize Q-table entry if state is new
    if state not in Q_TABLE:
        Q_TABLE[state] = {('left', r): 0 for r in range(ROWS)}
        Q_TABLE[state].update({('right', r): 0 for r in range(ROWS)})

    # Get list of valid actions
    valid_actions = [
        action for action in Q_TABLE[state]
        if EMPTY in board[action[1]]  
    ]

    if not valid_actions:
        print("AI has no valid moves left.")
        return board  

    # Choose action: 90% exploitation, 10% exploration
    if random.uniform(0, 1) < 0.1:
        action = random.choice(valid_actions)
        print(f"AI is exploring. Randomly picked: {action}")
    else:
        action = max(valid_actions, key=lambda a: Q_TABLE[state][a])
        print(f"AI is exploiting. Best known move: {action}")

    row, direction = action[1], action[0]

    # Make the move
    new_board, col = make_move(board, row, ai_symbol, direction)  # ✅ Uses ai_symbol

    if check_win(new_board, opponent):
        print(f"❌ AI ({ai_symbol}) stops: Opponent ({opponent}) has already won.")
        return new_board  

    # Convert new board state to a string
    new_state = str(new_board)

    # Reward based on AI symbol
    if check_win(new_board, ai_symbol):  
        reward = 10
        print(f"🎉 AI ({ai_symbol}) won! Rewarding move.")
    elif check_win(new_board, opponent):  
        reward = -10
        print(f"😞 AI ({ai_symbol}) lost. Penalizing move.")
    else:
        reward = -1  

    # Ensure the next state exists in Q-table
    if new_state not in Q_TABLE:
        Q_TABLE[new_state] = {('left', r): 0 for r in range(ROWS)}
        Q_TABLE[new_state].update({('right', r): 0 for r in range(ROWS)})

    # Find max Q-value for next state
    max_future_q = max(Q_TABLE[new_state].values())

    # Q-learning update formula
    Q_TABLE[state][action] = Q_TABLE[state][action] + ALPHA * (reward + GAMMA * max_future_q - Q_TABLE[state][action])

    # Save learning progress
    with open('q_table.pkl', 'wb') as f:
        pickle.dump(Q_TABLE, f)

    return new_board  
