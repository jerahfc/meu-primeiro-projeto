import tkinter as tk
import random

# ── Configurações ──────────────────────────────────────────────
WIDTH, HEIGHT = 600, 600
CELL         = 20
ROWS         = HEIGHT // CELL
COLS         = WIDTH  // CELL
SPEED        = 120          # ms entre cada frame

BG_COLOR     = "#1a1a2e"
GRID_COLOR   = "#16213e"
SNAKE_HEAD   = "#e94560"
SNAKE_BODY   = "#0f3460"
FOOD_COLOR   = "#f5a623"
TEXT_COLOR   = "#eaeaea"
BORDER_COLOR = "#e94560"

# ── Jogo ───────────────────────────────────────────────────────
class SnakeGame:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🐍 Snake Game")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)

        # Painel de pontuação
        self.score_var = tk.StringVar(value="Pontuação: 0")
        self.best_var  = tk.StringVar(value="Recorde: 0")
        self.best      = 0

        top = tk.Frame(root, bg=BG_COLOR)
        top.pack(pady=(10, 0))
        tk.Label(top, textvariable=self.score_var, font=("Consolas", 14, "bold"),
                 fg=SNAKE_HEAD, bg=BG_COLOR).pack(side="left", padx=20)
        tk.Label(top, textvariable=self.best_var,  font=("Consolas", 14, "bold"),
                 fg=FOOD_COLOR, bg=BG_COLOR).pack(side="left", padx=20)

        # Canvas
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                                bg=BG_COLOR, highlightthickness=2,
                                highlightbackground=BORDER_COLOR)
        self.canvas.pack(pady=10, padx=10)

        # Instruções
        tk.Label(root, text="← ↑ → ↓  mover   |   P  pausar   |   R  reiniciar",
                 font=("Consolas", 10), fg="#888", bg=BG_COLOR).pack(pady=(0, 8))

        # Bindings
        self.root.bind("<KeyPress>", self.on_key)

        self._init_state()
        self._draw_grid()
        self._start_screen()

    # ── Estado ─────────────────────────────────────────────────
    def _init_state(self):
        cx, cy        = COLS // 2, ROWS // 2
        self.snake    = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)
        self.next_dir  = (1, 0)
        self.score     = 0
        self.running   = False
        self.paused    = False
        self.game_over = False
        self._place_food()
        self.score_var.set("Pontuação: 0")

    def _place_food(self):
        while True:
            pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
            if pos not in self.snake:
                self.food = pos
                break

    # ── Telas ──────────────────────────────────────────────────
    def _start_screen(self):
        self._draw_grid()
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 - 30,
            text="🐍 SNAKE", font=("Consolas", 36, "bold"), fill=SNAKE_HEAD)
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 20,
            text="Pressione  ENTER  para jogar",
            font=("Consolas", 14), fill=TEXT_COLOR)
        self.root.bind("<Return>", lambda _: self._new_game())

    def _new_game(self):
        self.root.unbind("<Return>")
        self._init_state()
        self.running = True
        self._loop()

    def _show_game_over(self):
        overlay = self.canvas.create_rectangle(
            WIDTH // 4, HEIGHT // 3,
            WIDTH * 3 // 4, HEIGHT * 2 // 3,
            fill="#0f0f1a", outline=BORDER_COLOR, width=2)
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 - 30,
            text="FIM DE JOGO", font=("Consolas", 26, "bold"), fill=SNAKE_HEAD)
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 10,
            text=f"Pontuação: {self.score}", font=("Consolas", 14), fill=TEXT_COLOR)
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 40,
            text="R  para reiniciar", font=("Consolas", 12), fill=FOOD_COLOR)

    # ── Loop principal ─────────────────────────────────────────
    def _loop(self):
        if not self.running:
            return
        if self.paused:
            self.root.after(SPEED, self._loop)
            return

        self._update()
        self._render()

        if not self.game_over:
            self.root.after(SPEED, self._loop)

    def _update(self):
        self.direction = self.next_dir
        hx, hy = self.snake[0]
        dx, dy  = self.direction
        new_head = (hx + dx, hy + dy)

        # Colisão com parede
        if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
            self._end_game(); return

        # Colisão com o próprio corpo
        if new_head in self.snake:
            self._end_game(); return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 10
            if self.score > self.best:
                self.best = self.score
                self.best_var.set(f"Recorde: {self.best}")
            self.score_var.set(f"Pontuação: {self.score}")
            self._place_food()
        else:
            self.snake.pop()

    def _end_game(self):
        self.game_over = True
        self.running   = False
        self._render()
        self._show_game_over()

    # ── Renderização ───────────────────────────────────────────
    def _draw_grid(self):
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                x1, y1 = c * CELL, r * CELL
                self.canvas.create_rectangle(
                    x1, y1, x1 + CELL, y1 + CELL,
                    fill=GRID_COLOR, outline=BG_COLOR, width=1)

    def _render(self):
        self._draw_grid()

        # Comida (círculo laranja)
        fx, fy = self.food
        px, py = fx * CELL, fy * CELL
        pad = 3
        self.canvas.create_oval(
            px + pad, py + pad,
            px + CELL - pad, py + CELL - pad,
            fill=FOOD_COLOR, outline="")

        # Corpo da cobra
        for i, (sx, sy) in enumerate(self.snake):
            px, py = sx * CELL, sy * CELL
            color  = SNAKE_HEAD if i == 0 else SNAKE_BODY
            pad    = 1 if i > 0 else 0
            self.canvas.create_rectangle(
                px + pad + 1, py + pad + 1,
                px + CELL - pad - 1, py + CELL - pad - 1,
                fill=color, outline="")

        # Olhos na cabeça
        hx, hy = self.snake[0]
        dx, dy  = self.direction
        px, py  = hx * CELL, hy * CELL
        mid     = CELL // 2
        eye_r   = 2

        if dx == 1:   # direita
            e1 = (px + CELL - 5, py + 4)
            e2 = (px + CELL - 5, py + CELL - 6)
        elif dx == -1: # esquerda
            e1 = (px + 3, py + 4)
            e2 = (px + 3, py + CELL - 6)
        elif dy == -1: # cima
            e1 = (px + 4,        py + 3)
            e2 = (px + CELL - 6, py + 3)
        else:          # baixo
            e1 = (px + 4,        py + CELL - 5)
            e2 = (px + CELL - 6, py + CELL - 5)

        for ex, ey in (e1, e2):
            self.canvas.create_oval(ex, ey, ex + eye_r * 2, ey + eye_r * 2,
                                    fill="white", outline="")

        # Pausa
        if self.paused:
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2,
                text="⏸  PAUSADO  —  P para continuar",
                font=("Consolas", 16, "bold"), fill=TEXT_COLOR)

    # ── Controles ──────────────────────────────────────────────
    def on_key(self, event):
        key = event.keysym

        dirs = {
            "Up":    (0, -1), "w": (0, -1),
            "Down":  (0,  1), "s": (0,  1),
            "Left":  (-1, 0), "a": (-1, 0),
            "Right": (1,  0), "d": (1,  0),
        }

        if key in dirs:
            nd = dirs[key]
            # Impede inversão de direção
            if (nd[0] != -self.direction[0] or nd[1] != -self.direction[1]):
                self.next_dir = nd

        elif key.lower() == "p" and self.running:
            self.paused = not self.paused
            if not self.paused:
                self._render()

        elif key.lower() == "r":
            self.running = False
            self.root.after(50, self._new_game)

# ── Main ───────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()