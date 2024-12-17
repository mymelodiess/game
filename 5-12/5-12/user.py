import json
from datetime import datetime
import os

def check_username(username):
    try:
        with open('users.json', 'r') as file:
            users = json.load(file)
    except FileNotFoundError:
        users = []

    if username in users:
        return True
    else:
        users.append(username)
        with open('users.json', 'w') as file:
            json.dump(users, file)
        return False

def save_game_history(username, difficulty, time, status):
    history_entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "difficulty": difficulty,
        "time": time,
        "status": status
    }

    try:
        with open('history.json', 'r') as file:
            history = json.load(file)
    except FileNotFoundError:
        history = {}

    if username not in history:
        history[username] = []

    history[username].append(history_entry)

    with open('history.json', 'w') as file:
        json.dump(history, file, indent=4)

def get_game_history(username):
    try:
        with open('history.json', 'r') as file:
            history = json.load(file)
    except FileNotFoundError:
        return []

    return history.get(username, [])

def save_game_state(app, board, difficulty):
    game_state = {
        "username": app.username,
        "difficulty": difficulty,
        "time": app.start_time,
        "errors": app.errors,
        "board": [[cell.text() if cell.text() else 0 for cell in row] for row in app.cells],
        "user_input": [[not cell.isReadOnly() for cell in row] for row in app.cells],
        "remaining_counts": app.remaining_counts
    }

    with open(f'{app.username}_game_state.json', 'w') as file:
        json.dump(game_state, file, indent=4)

def load_game_state(username):
    try:
        with open(f'{username}_game_state.json', 'r') as file:
            game_state = json.load(file)
            game_state["board"] = [[int(cell) if cell != 0 else 0 for cell in row] for row in game_state["board"]]
            return game_state
    except FileNotFoundError:
        return None

def delete_game_state(username):
    try:
        os.remove(f'{username}_game_state.json')
    except FileNotFoundError:
        pass