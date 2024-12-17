# ui.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QGridLayout, QTableWidget, QTableWidgetItem, QHBoxLayout, QSpacerItem, QSizePolicy, QDesktopWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDesktopWidget
from sudoku import generate_sudoku_board, display_sudoku
from user import check_username, get_game_history, save_game_state, load_game_state
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class SudokuApp(QWidget):
    def __init__(self):
        super().__init__()
        self.sudoku_grid_layout = None
        self.selected_cell = None
        self.number_buttons_layout = None
        self.timer = None
        self.initUI()
        self.center()

    def center(self):
        self.setGeometry(0, 0, QDesktopWidget().availableGeometry().width(), QDesktopWidget().availableGeometry().height())
        self.move(0, 0)

    def initUI(self):
        self.setWindowTitle('Sudoku App')
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)
        self.setStyleSheet("""
            QWidget {
                font-family: 'Helvetica Neue', Arial, sans-serif;
                font-size: 20px;
                background-color: #f0f0f0;
                font-weight: bold;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 24px;
                margin: 15px 10px;
                cursor: pointer;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit {
                border: 2px solid #4CAF50;
                border-radius: 5px;
                padding: 15px;
                font-size: 24px;
                text-align: center;
                font-weight: bold;
            }
            QLabel {
                font-weight: bold;
            }
        """)
        self.show_username_input()

    def add_logo(self):
        logo = QLabel('🧩 Sudoku 🧩', self)
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: #4CAF50;
                margin: 20px;
            }
        """)
        self.layout.addWidget(logo)
    
    def show_username_input(self):
        self.clear_layout()
        self.add_logo()

        self.label = QLabel('Enter your username:', self)
        self.layout.addWidget(self.label)

        self.username_input = QLineEdit(self)
        self.username_input.setFixedWidth(350)
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 15px;
                margin: 15px 0;
                font-size: 28px;
                border: 2px solid #4CAF50;
                border-radius: 5px;
            }
        """)
        self.layout.addWidget(self.username_input)

        self.submit_button = QPushButton('Submit', self)
        self.submit_button.setFixedWidth(350)
        self.submit_button.setStyleSheet("""
            QPushButton {
                padding: 15px;
                margin: 15px 0;
                font-size: 28px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.submit_button.clicked.connect(self.check_username)
        self.layout.addWidget(self.submit_button)
    
    def show_main_menu(self):
        self.clear_layout()
        

        play_button = QPushButton('Play', self)
        play_button.clicked.connect(self.show_difficulty_levels)
        self.layout.addWidget(play_button)

        if os.path.exists(f'{self.username}_game_state.json'):
            continue_button = QPushButton('Continue', self)
            continue_button.clicked.connect(self.continue_game)
            self.layout.addWidget(continue_button)

        history_button = QPushButton('View History', self)
        history_button.clicked.connect(self.show_game_history)
        self.layout.addWidget(history_button)

        stats_button = QPushButton('Statistics', self)
        stats_button.clicked.connect(self.show_statistics)
        self.layout.addWidget(stats_button)

        exit_button = QPushButton('Exit', self)
        exit_button.clicked.connect(self.close)
        self.layout.addWidget(exit_button)

    def check_username(self):
        username = self.username_input.text()
        if not username:
            QMessageBox.warning(self, 'Warning', 'Please enter a username')
            return

        if check_username(username):
            QMessageBox.information(self, 'Welcome', f'Welcome back, {username}!')
        else:
            QMessageBox.information(self, 'Welcome', f'Hello, new user {username}!')

        self.username = username
        self.show_main_menu()

    def show_main_menu(self):
        self.clear_layout()

        play_button = QPushButton('Play', self)
        play_button.clicked.connect(self.show_difficulty_levels)
        self.layout.addWidget(play_button)

        if os.path.exists(f'{self.username}_game_state.json'):
            continue_button = QPushButton('Continue', self)
            continue_button.clicked.connect(self.continue_game)
            self.layout.addWidget(continue_button)

        history_button = QPushButton('View History', self)
        history_button.clicked.connect(self.show_game_history)
        self.layout.addWidget(history_button)

        stats_button = QPushButton('Statistics', self)
        stats_button.clicked.connect(self.show_statistics)
        self.layout.addWidget(stats_button)

        exit_button = QPushButton('Exit', self)
        exit_button.clicked.connect(self.close)
        self.layout.addWidget(exit_button)

    def clear_layout(self):
        if self.timer:
            self.timer.stop()

        if self.sudoku_grid_layout:
            for i in reversed(range(self.sudoku_grid_layout.count())):
                widget = self.sudoku_grid_layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()
            self.sudoku_grid_layout = None

        if self.number_buttons_layout:
            for i in reversed(range(self.number_buttons_layout.count())):
                widget = self.number_buttons_layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()
            self.number_buttons_layout = None

        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

    def show_difficulty_levels(self):
        self.clear_layout()

        easy_button = QPushButton('Easy', self)
        easy_button.clicked.connect(lambda: self.load_sudoku("easy"))
        self.layout.addWidget(easy_button)

        medium_button = QPushButton('Medium', self)
        medium_button.clicked.connect(lambda: self.load_sudoku("medium"))
        self.layout.addWidget(medium_button)

        hard_button = QPushButton('Hard', self)
        hard_button.clicked.connect(lambda: self.load_sudoku("hard"))
        self.layout.addWidget(hard_button)

        back_button = QPushButton('Back', self)
        back_button.clicked.connect(self.show_main_menu)
        self.layout.addWidget(back_button)

    def load_sudoku(self, difficulty):
        board = generate_sudoku_board(difficulty)
        display_sudoku(self, board, difficulty)

    def continue_game(self):
        game_state = load_game_state(self.username)
        if game_state:
            self.start_time = game_state["time"]
            self.errors = game_state["errors"]
            self.remaining_counts = game_state["remaining_counts"]
            board = game_state["board"]
            difficulty = game_state["difficulty"]
            user_input = game_state["user_input"]
            display_sudoku(self, board, difficulty, start_time=self.start_time, errors=self.errors, remaining_counts=self.remaining_counts, user_input=user_input)

    def handle_number_click(self, number):
        if self.selected_cell:
            self.selected_cell.setText(str(number))
            self.remaining_counts[number] -= 1
            self.update_remaining_counts()

    def update_remaining_counts(self):
        for i in range(1, 10):
            button = self.number_buttons[i-1]
            button.setText(f"{i}")

    def show_game_history(self):
        self.clear_layout()

        history = get_game_history(self.username)

        history_label = QLabel('Game History:', self)
        self.layout.addWidget(history_label)

        if not history:
            no_history_label = QLabel('No game history available.', self)
            self.layout.addWidget(no_history_label)
        else:
            history_table = QTableWidget(self)
            history_table.setColumnCount(4)
            history_table.setHorizontalHeaderLabels(['Date', 'Difficulty', 'Time (s)', 'Status'])
            history_table.setRowCount(len(history))

            for row, entry in enumerate(history):
                history_table.setItem(row, 0, QTableWidgetItem(entry['date']))
                history_table.setItem(row, 1, QTableWidgetItem(entry['difficulty']))
                history_table.setItem(row, 2, QTableWidgetItem(str(entry['time'])))
                history_table.setItem(row, 3, QTableWidgetItem(entry['status']))

            history_table.resizeColumnsToContents()
            self.layout.addWidget(history_table)

        back_button = QPushButton('Back', self)
        back_button.clicked.connect(self.show_main_menu)
        self.layout.addWidget(back_button)

    def show_statistics(self):
        self.clear_layout()

        history = get_game_history(self.username)

        if not history:
            no_stats_label = QLabel('No statistics available.', self)
            self.layout.addWidget(no_stats_label)
        else:
            total_games = len(history)
            wins = sum(1 for game in history if game['status'] == 'Win')
            losses = total_games - wins
            best_times = {'easy': float('inf'), 'medium': float('inf'), 'hard': float('inf')}
            worst_times = {'easy': 0, 'medium': 0, 'hard': 0}
            total_times = {'easy': 0, 'medium': 0, 'hard': 0}
            count_times = {'easy': 0, 'medium': 0, 'hard': 0}

            for game in history:
                if game['status'] == 'Win':
                    if game['time'] < best_times[game['difficulty']]:
                        best_times[game['difficulty']] = game['time']
                    if game['time'] > worst_times[game['difficulty']]:
                        worst_times[game['difficulty']] = game['time']
                    total_times[game['difficulty']] += game['time']
                    count_times[game['difficulty']] += 1

            average_times = {k: (total_times[k] / count_times[k] if count_times[k] != 0 else 0) for k in total_times}
            best_times = {k: (v if v != float('inf') else 0) for k, v in best_times.items()}
            worst_times = {k: (v if v != 0 else 0) for k, v in worst_times.items()}

            labels = 'Wins', 'Losses'
            sizes = [wins, losses]
            colors = ['#4CAF50', '#FF6347']
            explode = (0.1, 0)

            fig = Figure(figsize=(14, 8))
            ax1 = fig.add_subplot(121)
            ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
            ax1.axis('equal')
            ax1.set_title('Win/Loss Ratio')

            ax2 = fig.add_subplot(122)
            difficulties = ['Easy', 'Medium', 'Hard']
            best = [best_times['easy'], best_times['medium'], best_times['hard']]
            worst = [worst_times['easy'], worst_times['medium'], worst_times['hard']]
            avg = [average_times['easy'], average_times['medium'], average_times['hard']]
            bar_width = 0.2
            index = range(len(difficulties))

            bars_best = ax2.bar(index, best, bar_width, label='Best Time')
            bars_worst = ax2.bar([i + bar_width for i in index], worst, bar_width, label='Worst Time')
            bars_avg = ax2.bar([i + 2 * bar_width for i in index], avg, bar_width, label='Average Time')

            ax2.set_xlabel('Difficulty')
            ax2.set_ylabel('Time (s)')
            ax2.set_title('Best, Worst, and Average Times by Difficulty')
            ax2.set_xticks([i + bar_width for i in index])
            ax2.set_xticklabels(difficulties)
            ax2.legend()

            for bar in bars_best:
                yval = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), ha='center', va='bottom')

            for bar in bars_worst:
                yval = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), ha='center', va='bottom')

            for bar in bars_avg:
                yval = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), ha='center', va='bottom')

            total_games_label = QLabel(f'Total Games: {total_games}', self)
            wins_label = QLabel(f'Wins: {wins}', self)
            losses_label = QLabel(f'Losses: {losses}', self)
            self.layout.addWidget(total_games_label)
            self.layout.addWidget(wins_label)
            self.layout.addWidget(losses_label)

            canvas = FigureCanvas(fig)
            self.layout.addWidget(canvas)

        back_button = QPushButton('Back', self)
        back_button.clicked.connect(self.show_main_menu)
        self.layout.addWidget(back_button)