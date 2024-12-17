import random
from PyQt5.QtWidgets import QLineEdit, QGridLayout, QPushButton, QFrame, QMessageBox, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from user import save_game_history, save_game_state
import os

def generate_sudoku_board(difficulty):
    base = 3
    side = base * base

    def pattern(r, c): return (base*(r % base)+r//base+c) % side
    def shuffle(s): return random.sample(s, len(s))

    rBase = range(base)
    rows = [g*base + r for g in shuffle(rBase) for r in shuffle(rBase)]
    cols = [g*base + c for g in shuffle(rBase) for c in shuffle(rBase)]
    nums = shuffle(range(1, base*base+1))

    board = [[nums[pattern(r, c)] for c in cols] for r in rows]

    squares = side*side
    empties = squares * 3//4 if difficulty == "hard" else squares * 2//3 if difficulty == "medium" else squares * 1//2
    for p in random.sample(range(squares), empties):
        board[p//side][p % side] = 0

    return board

def is_valid_move(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def solve_sudoku(board):
    empty = find_empty_location(board)
    if not empty:
        return True
    row, col = empty

    for num in range(1, 10):
        if is_valid_move(board, row, col, num):
            board[row][col] = num
            if solve_sudoku(board):
                return True
            board[row][col] = 0

    return False

def find_empty_location(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                return (row, col)
    return None

def update_timer(app):
    app.start_time += 1
    app.timer_label.setText(f"Time: {app.start_time}s")
    if app.start_time > 100000:
        app.timer.stop()
        QMessageBox.warning(app, 'Game Over', 'You have exceeded the time limit. You lose!')
        save_game_history(app.username, app.difficulty, app.start_time, "Lose")
        app.show_difficulty_levels()
        if os.path.exists(f'{app.username}_game_state.json'):
            os.remove(f'{app.username}_game_state.json')

def display_sudoku(app, board, difficulty, start_time=0, errors=0, remaining_counts=None, user_input=None):
    app.clear_layout()

    app.sudoku_grid_layout = QGridLayout()
    app.sudoku_grid_layout.setSpacing(1)
    app.selected_cell = None
    app.errors = errors
    app.start_time = start_time
    app.timer = QTimer()
    app.timer.timeout.connect(lambda: update_timer(app))
    app.timer.start(1000)

    app.difficulty = difficulty

    if remaining_counts is None:
        app.remaining_counts = {i: 9 for i in range(1, 10)}
        for row in board:
            for num in row:
                if num != 0:
                    app.remaining_counts[num] -= 1
    else:
        app.remaining_counts = remaining_counts

    def select_cell(event, cell):
        app.selected_cell = cell

    def validate_input(cell, row, col):
        text = cell.text()
        if text.isdigit() and 1 <= int(text) <= 9:
            num = int(text)
            if num not in app.remaining_counts:
                app.remaining_counts[num] = 9
            if is_valid_move(board, row, col, num):
                if board[row][col] != 0:
                    app.remaining_counts[board[row][col]] += 1
                board[row][col] = num
                app.remaining_counts[num] -= 1
                app.update_remaining_counts()
                
                # Lock the cell after valid input
                cell.setReadOnly(True)
                cell.setStyleSheet("""
                    QLineEdit {
                        background-color: #e8f5e9;  /* Light green background */
                        color: #2e7d32;  /* Dark green text */
                        font-weight: bold;
                    }
                """)
                
                if not find_empty_location(board):
                    app.timer.stop()
                    QMessageBox.information(app, 'Congratulations', 'You have solved the Sudoku puzzle!')
                    save_game_history(app.username, difficulty, app.start_time, "Win")
                    app.show_difficulty_levels()
                    if os.path.exists(f'{app.username}_game_state.json'):
                        os.remove(f'{app.username}_game_state.json')
            else:
                QMessageBox.warning(app, 'Invalid Move', 'This move is not valid.')
                cell.blockSignals(True)
                cell.setText("")
                cell.blockSignals(False)
                app.errors += 1
                app.error_label.setText(f"Errors: {app.errors}")
                if app.errors > 3:
                    app.timer.stop()
                    QMessageBox.warning(app, 'Game Over', 'You have made too many mistakes. You lose!')
                    save_game_history(app.username, difficulty, app.start_time, "Lose")
                    app.show_difficulty_levels()
                    if os.path.exists(f'{app.username}_game_state.json'):
                        os.remove(f'{app.username}_game_state.json')
        else:
            QMessageBox.warning(app, 'Invalid Input', 'Please enter a number between 1 and 9.')
            cell.blockSignals(True)
            cell.setText("")
            cell.blockSignals(False)
            app.errors += 1
            app.error_label.setText(f"Errors: {app.errors}")
            if app.errors > 3:
                app.timer.stop()
                QMessageBox.warning(app, 'Game Over', 'You have made too many mistakes. You lose!')
                save_game_history(app.username, difficulty, app.start_time, "Lose")
                app.show_difficulty_levels()
                if os.path.exists(f'{app.username}_game_state.json'):
                    os.remove(f'{app.username}_game_state.json')

    app.cells = []
    for row in range(9):
        row_cells = []
        for col in range(9):
            cell = QLineEdit(app)
            # Set alignment and size
            cell.setAlignment(Qt.AlignCenter)
            cell.setFixedSize(60, 60)
            border_style = "border: 1px solid #4CAF50;"

            if row % 3 == 0:
                border_style += "border-top: 3px solid #0000FF;"
            if col % 3 == 0:
                border_style += "border-left: 3px solid #0000FF;"
            if row == 8:
                border_style += "border-bottom: 3px solid #0000FF;"
            if col == 8:
                border_style += "border-right: 3px solid #0000FF;"

            cell.setStyleSheet(f"""
                QLineEdit {{
                    {border_style}
                    font-size: 24px;
                    background-color: #ffffff;
                    font-weight: bold;
                }}
                QLineEdit[readOnly="true"] {{
                    background-color: #e0e0e0;
                }}
            """)

            cell.mousePressEvent = lambda event, cell=cell: select_cell(event, cell)
            if board[row][col] != 0:
                cell.setText(str(board[row][col]))
                if user_input and user_input[row][col]:
                    cell.setReadOnly(False)
                else:
                    cell.setReadOnly(True)
            cell.textChanged.connect(lambda _, cell=cell, row=row, col=col: validate_input(cell, row, col))
            app.sudoku_grid_layout.addWidget(cell, row, col)
            row_cells.append(cell)
        app.cells.append(row_cells)

    app.layout.addLayout(app.sudoku_grid_layout)

    app.number_buttons_layout = QGridLayout()
    app.number_buttons_layout.setSpacing(10)
    app.number_buttons = []
    for i in range(1, 10):
        button = QPushButton(f"{i}", app)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 15px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 18px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
        """)
        button.clicked.connect(lambda _, num=i: app.handle_number_click(num))
        app.number_buttons_layout.addWidget(button, (i-1)//3, (i-1)%3)
        app.number_buttons.append(button)

    app.layout.addLayout(app.number_buttons_layout)

    solve_button = QPushButton('Solve Sudoku', app)
    solve_button.setStyleSheet(f"""
        QPushButton {{
            background-color: #2196F3;
            color: white;
            border: none;
            padding: 15px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 18px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 8px;
        }}
        QPushButton:hover {{
            background-color: #1976D2;
        }}
    """)
    solve_button.clicked.connect(lambda: solve_and_display(app, board, difficulty))
    app.layout.addWidget(solve_button)

    save_button = QPushButton('Save Game', app)
    save_button.setStyleSheet(f"""
        QPushButton {{
            background-color: #FF9800;
            color: white;
            border: none;
            padding: 15px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 18px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 8px;
        }}
        QPushButton:hover {{
            background-color: #FB8C00;
        }}
    """)
    save_button.clicked.connect(lambda: save_and_confirm(app, board, difficulty))
    app.layout.addWidget(save_button)

    def handle_back():
        reply = QMessageBox.question(app, 'Save Game', 
                                   'Do you want to save the game before leaving?',
                                   QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        
        if reply == QMessageBox.Yes:
            save_game_state(app, board, difficulty)
            app.show_difficulty_levels()
        elif reply == QMessageBox.No:
            if os.path.exists(f'{app.username}_game_state.json'):
                os.remove(f'{app.username}_game_state.json')
            app.show_difficulty_levels()
        # If Cancel, do nothing and stay in game
    
    back_button = QPushButton('Back', app)
    back_button.setStyleSheet(f"""
        QPushButton {{
            background-color: #f44336;
            color: white;
            border: none;
            padding: 15px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 18px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 8px;
        }}
        QPushButton:hover {{
            background-color: #d32f2f;
        }}
    """)
    back_button.clicked.connect(handle_back)
    app.layout.addWidget(back_button)

    app.timer_label = QLabel(f"Time: {app.start_time}s", app)
    app.layout.addWidget(app.timer_label)

    app.error_label = QLabel(f"Errors: {app.errors}", app)
    app.layout.addWidget(app.error_label)

def save_and_confirm(app, board, difficulty):
    save_game_state(app, board, difficulty)
    QMessageBox.information(app, 'Saved', 'Game has been saved successfully.')

def solve_and_display(app, board, difficulty):
    start_time = app.start_time
    if solve_sudoku(board):
        for row in range(9):
            for col in range(9):
                cell = app.cells[row][col]
                if not cell.isReadOnly():
                    cell.blockSignals(True)
                    cell.setText(str(board[row][col]))
                    cell.blockSignals(False)
        app.timer.stop()
        QMessageBox.information(app, 'Congratulations', 'You have solved the Sudoku puzzle!')
        save_game_history(app.username, difficulty, app.start_time, "Win")
        app.show_difficulty_levels()
    else:
        app.timer.stop()
        QMessageBox.warning(app, 'Unsolvable', 'This Sudoku puzzle cannot be solved.')
        save_game_history(app.username, difficulty, app.start_time, "Lose")

    if os.path.exists(f'{app.username}_game_state.json'):
        os.remove(f'{app.username}_game_state.json')