from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
import random

# Color Palette (Flat Design)
COLOR_BG = get_color_from_hex("#2C3E50")      # Dark Blue-Grey
COLOR_BTN = get_color_from_hex("#34495E")     # Slightly lighter
COLOR_BTN_PRESS = get_color_from_hex("#2980B9") # Blue highlight
COLOR_X = get_color_from_hex("#E74C3C")       # Red
COLOR_O = get_color_from_hex("#F1C40F")       # Yellow
COLOR_WIN = get_color_from_hex("#2ECC71")     # Green
COLOR_TEXT = get_color_from_hex("#ECF0F1")    # White

WIN_COMBOS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # cols
    (0, 4, 8), (2, 4, 6)              # diagonals
]

class TicTacToe(App):
    def build(self):
        Window.clearcolor = COLOR_BG
        self.title = "Ultimate Tic-Tac-Toe"
        
        # Game State
        self.player = "X"
        self.moves = [""] * 9
        self.game_over = False
        self.score_x = 0
        self.score_o = 0
        self.ai_mode = True # Default to AI mode
        
        # Main Layout
        root = BoxLayout(orientation="vertical", padding=20, spacing=20)
        
        # Header (Scoreboard & Mode)
        header = BoxLayout(orientation="vertical", size_hint_y=None, height=120, spacing=10)
        
        self.score_label = Label(
            text=f"X: {self.score_x} | O: {self.score_o}",
            font_size=40,
            bold=True,
            color=COLOR_TEXT
        )
        header.add_widget(self.score_label)
        
        self.mode_btn = Button(
            text="Mode: Single Player (vs AI)",
            size_hint=(None, None),
            size=(300, 50),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=COLOR_BTN_PRESS,
            color=COLOR_TEXT
        )
        self.mode_btn.bind(on_press=self.toggle_mode)
        header.add_widget(self.mode_btn)
        
        self.info = Label(text="Player X's Turn", font_size=24, color=COLOR_TEXT)
        header.add_widget(self.info)
        
        root.add_widget(header)

        # Grid
        self.grid = GridLayout(cols=3, spacing=10, size_hint=(.8, .6), pos_hint={'center_x': 0.5})
        self.buttons = []
        for i in range(9):
            btn = Button(
                text="",
                font_size=60,
                background_normal='',
                background_color=COLOR_BTN,
                bold=True
            )
            btn.index = i
            btn.bind(on_press=self.on_press)
            self.buttons.append(btn)
            self.grid.add_widget(btn)
        root.add_widget(self.grid)

        # Controls
        control_bar = BoxLayout(size_hint_y=None, height=60, spacing=10)
        reset_btn = Button(
            text="Restart Game",
            font_size=20,
            background_normal='',
            background_color=COLOR_BTN_PRESS,
            color=COLOR_TEXT
        )
        reset_btn.bind(on_press=self.reset_game)
        control_bar.add_widget(reset_btn)
        root.add_widget(control_bar)

        return root

    def toggle_mode(self, btn):
        self.ai_mode = not self.ai_mode
        mode_text = "Single Player (vs AI)" if self.ai_mode else "2 Player (PvP)"
        btn.text = f"Mode: {mode_text}"
        self.reset_game()

    def on_press(self, btn):
        if self.game_over or btn.text != "":
            return

        self.make_move(btn.index, self.player)

        if not self.game_over and self.ai_mode and self.player == "O":
            # Small delay for AI move to feel natural
            Clock.schedule_once(self.ai_move, 0.3)

    def make_move(self, index, player):
        self.moves[index] = player
        btn = self.buttons[index]
        btn.text = player
        btn.color = COLOR_X if player == "X" else COLOR_O
        
        if self.check_winner(player):
            self.end_game(f"Player {player} Wins! 🎉")
            if player == "X":
                self.score_x += 1
            else:
                self.score_o += 1
            self.update_score()
            return
            
        if all(m != "" for m in self.moves):
            self.end_game("It's a Draw! 🤝")
            return
            
        self.switch_player()

    def switch_player(self):
        self.player = "O" if self.player == "X" else "X"
        self.info.text = f"Player {self.player}'s Turn"

    def ai_move(self, dt):
        if self.game_over:
            return
        
        # Minimax AI Implementation
        best_score = -float('inf')
        move = -1
        
        # Check center first for better performance/start
        available_moves = [i for i, m in enumerate(self.moves) if m == ""]
        
        # Simple optimization: If start, pick center or corner
        if len(available_moves) == 9:
            move = 4
        elif len(available_moves) == 8 and self.moves[4] == "":
             move = 4
        else:
            for i in available_moves:
                self.moves[i] = "O"
                score = self.minimax(self.moves, 0, False)
                self.moves[i] = ""
                if score > best_score:
                    best_score = score
                    move = i
        
        if move != -1:
            self.make_move(move, "O")

    def minimax(self, board, depth, is_maximizing):
        # AI is 'O' (maximizing), Human is 'X' (minimizing)
        if self.check_win_simulation(board, "O"):
            return 10 - depth
        if self.check_win_simulation(board, "X"):
            return depth - 10
        if "" not in board:
            return 0
        
        if is_maximizing:
            best_score = -float('inf')
            for i in range(9):
                if board[i] == "":
                    board[i] = "O"
                    score = self.minimax(board, depth + 1, False)
                    board[i] = ""
                    best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for i in range(9):
                if board[i] == "":
                    board[i] = "X"
                    score = self.minimax(board, depth + 1, True)
                    board[i] = ""
                    best_score = min(score, best_score)
            return best_score

    def check_win_simulation(self, board, p):
        for a, b, c in WIN_COMBOS:
            if board[a] == board[b] == board[c] == p:
                return True
        return False

    def check_winner(self, p):
        for a, b, c in WIN_COMBOS:
            if self.moves[a] == self.moves[b] == self.moves[c] == p:
                for i in (a, b, c):
                    self.buttons[i].background_color = COLOR_WIN
                return True
        return False

    def end_game(self, message):
        self.info.text = message
        self.game_over = True

    def update_score(self):
        self.score_label.text = f"X: {self.score_x} | O: {self.score_o}"

    def reset_game(self, *_):
        self.player = "X"
        self.moves = [""] * 9
        self.game_over = False
        self.info.text = "Player X's Turn"
        for btn in self.buttons:
            btn.text = ""
            btn.background_color = COLOR_BTN
            btn.color = COLOR_TEXT

if __name__ == "__main__":
    TicTacToe().run()