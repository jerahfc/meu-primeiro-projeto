import tkinter as tk
import random
import time

# === CONFIGURAÇÕES ===
COLS = 10
ROWS = 20
CELL = 32
PANEL_W = 180
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL

COLORS = {
    'I': '#00F5FF',
    'O': '#FFE500',
    'T': '#BF00FF',
    'S': '#00FF6A',
    'Z': '#FF2D55',
    'J': '#FF8C00',
    'L': '#0080FF',
    'ghost': '#ffffff22',
    'bg': '#0A0A0F',
    'grid': '#1A1A2E',
    'panel': '#0D0D1A',
    'text': '#E0E0FF',
    'accent': '#00F5FF',
}

SHAPES = {
    'I': [[(0,1),(1,1),(2,1),(3,1)],
          [(2,0),(2,1),(2,2),(2,3)],
          [(0,2),(1,2),(2,2),(3,2)],
          [(1,0),(1,1),(1,2),(1,3)]],

    'O': [[(1,0),(2,0),(1,1),(2,1)]]*4,

    'T': [[(0,1),(1,1),(2,1),(1,0)],
          [(1,0),(1,1),(1,2),(2,1)],
          [(0,1),(1,1),(2,1),(1,2)],
          [(1,0),(1,1),(1,2),(0,1)]],

    'S': [[(1,0),(2,0),(0,1),(1,1)],
          [(1,0),(1,1),(2,1),(2,2)],
          [(1,1),(2,1),(0,2),(1,2)],
          [(0,0),(0,1),(1,1),(1,2)]],

    'Z': [[(0,0),(1,0),(1,1),(2,1)],
          [(2,0),(1,1),(2,1),(1,2)],
          [(0,1),(1,1),(1,2),(2,2)],
          [(1,0),(0,1),(1,1),(0,2)]],

    'J': [[(0,0),(0,1),(1,1),(2,1)],
          [(1,0),(2,0),(1,1),(1,2)],
          [(0,1),(1,1),(2,1),(2,2)],
          [(1,0),(1,1),(0,2),(1,2)]],

    'L': [[(2,0),(0,1),(1,1),(2,1)],
          [(1,0),(1,1),(1,2),(2,2)],
          [(0,1),(1,1),(2,1),(0,2)],
          [(0,0),(1,0),(1,1),(1,2)]],
}

KICK_DATA = {
    'normal': {
        (0,1): [(0,0),(-1,0),(-1,1),(0,-2),(-1,-2)],
        (1,0): [(0,0),(1,0),(1,-1),(0,2),(1,2)],
        (1,2): [(0,0),(1,0),(1,-1),(0,2),(1,2)],
        (2,1): [(0,0),(-1,0),(-1,1),(0,-2),(-1,-2)],
        (2,3): [(0,0),(1,0),(1,1),(0,-2),(1,-2)],
        (3,2): [(0,0),(-1,0),(-1,-1),(0,2),(-1,2)],
        (3,0): [(0,0),(-1,0),(-1,-1),(0,2),(-1,2)],
        (0,3): [(0,0),(1,0),(1,1),(0,-2),(1,-2)],
    },
    'I': {
        (0,1): [(0,0),(-2,0),(1,0),(-2,-1),(1,2)],
        (1,0): [(0,0),(2,0),(-1,0),(2,1),(-1,-2)],
        (1,2): [(0,0),(-1,0),(2,0),(-1,2),(2,-1)],
        (2,1): [(0,0),(1,0),(-2,0),(1,-2),(-2,1)],
        (2,3): [(0,0),(2,0),(-1,0),(2,1),(-1,-2)],
        (3,2): [(0,0),(-2,0),(1,0),(-2,-1),(1,2)],
        (3,0): [(0,0),(1,0),(-2,0),(1,-2),(-2,1)],
        (0,3): [(0,0),(-1,0),(2,0),(-1,2),(2,-1)],
    }
}


class Piece:
    def __init__(self, shape=None):
        self.shape = shape or random.choice(list(SHAPES.keys()))
        self.rot = 0
        self.x = 3
        self.y = 0

    def cells(self, x=None, y=None, rot=None):
        x = self.x if x is None else x
        y = self.y if y is None else y
        rot = self.rot if rot is None else rot
        return [(x + dx, y + dy) for dx, dy in SHAPES[self.shape][rot % 4]]

    def color(self):
        return COLORS[self.shape]


class Tetris:
    def __init__(self, root):
        self.root = root
        self.root.title("TETRIS")
        self.root.configure(bg=COLORS['bg'])
        self.root.resizable(False, False)

        self._build_ui()
        self.reset()
        self.root.bind('<Key>', self.on_key)
        self.root.focus_set()

    def _build_ui(self):
        container = tk.Frame(self.root, bg=COLORS['bg'])
        container.pack(padx=20, pady=20)

        # Canvas principal
        self.canvas = tk.Canvas(
            container, width=WIDTH, height=HEIGHT,
            bg=COLORS['bg'], highlightthickness=2,
            highlightbackground=COLORS['accent']
        )
        self.canvas.grid(row=0, column=0, padx=(0, 16))

        # Painel lateral
        self.panel = tk.Canvas(
            container, width=PANEL_W, height=HEIGHT,
            bg=COLORS['panel'], highlightthickness=1,
            highlightbackground='#2A2A4A'
        )
        self.panel.grid(row=0, column=1, sticky='n')

    def reset(self):
        self.board = [[None]*COLS for _ in range(ROWS)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.combo = 0
        self.game_over = False
        self.paused = False
        self.current = Piece()
        self.next_piece = Piece()
        self.hold = None
        self.hold_used = False
        self._schedule_drop()
        self.draw()

    def _drop_interval(self):
        return max(80, 500 - (self.level - 1) * 40)

    def _schedule_drop(self):
        if hasattr(self, '_drop_id'):
            self.root.after_cancel(self._drop_id)
        self._drop_id = self.root.after(self._drop_interval(), self._auto_drop)

    def _auto_drop(self):
        if not self.game_over and not self.paused:
            self.move(0, 1)
        self._schedule_drop()

    def valid(self, piece, x=None, y=None, rot=None):
        for cx, cy in piece.cells(x, y, rot):
            if cx < 0 or cx >= COLS or cy >= ROWS:
                return False
            if cy >= 0 and self.board[cy][cx]:
                return False
        return True

    def ghost_y(self):
        y = self.current.y
        while self.valid(self.current, y=y+1):
            y += 1
        return y

    def move(self, dx, dy):
        nx, ny = self.current.x + dx, self.current.y + dy
        if self.valid(self.current, x=nx, y=ny):
            self.current.x, self.current.y = nx, ny
            self.draw()
            return True
        elif dy > 0:
            self.lock()
        return False

    def rotate(self, dir=1):
        old_rot = self.current.rot
        new_rot = (old_rot + dir) % 4
        key = (old_rot, new_rot)
        kicks = KICK_DATA['I' if self.current.shape == 'I' else 'normal'].get(key, [(0,0)])
        for kx, ky in kicks:
            nx = self.current.x + kx
            ny = self.current.y - ky
            if self.valid(self.current, x=nx, y=ny, rot=new_rot):
                self.current.x, self.current.y = nx, ny
                self.current.rot = new_rot
                self.draw()
                return

    def hard_drop(self):
        gy = self.ghost_y()
        self.score += (gy - self.current.y) * 2
        self.current.y = gy
        self.lock()

    def soft_drop(self):
        if self.move(0, 1):
            self.score += 1

    def hold_piece(self):
        if self.hold_used:
            return
        if self.hold is None:
            self.hold = Piece(self.current.shape)
            self.current = self.next_piece
            self.next_piece = Piece()
        else:
            old_shape = self.hold.shape
            self.hold = Piece(self.current.shape)
            self.current = Piece(old_shape)
        self.hold_used = True
        self.draw()

    def lock(self):
        for cx, cy in self.current.cells():
            if cy < 0:
                self.game_over = True
                self.draw()
                return
            self.board[cy][cx] = self.current.color()

        cleared = self._clear_lines()
        self._update_score(cleared)
        self.current = self.next_piece
        self.next_piece = Piece()
        self.hold_used = False
        self.draw()

    def _clear_lines(self):
        full = [r for r in range(ROWS) if all(self.board[r])]
        for r in full:
            del self.board[r]
            self.board.insert(0, [None]*COLS)
        return len(full)

    def _update_score(self, cleared):
        base = [0, 100, 300, 500, 800]
        if cleared:
            self.combo += 1
            bonus = 50 * self.combo * self.level
            self.score += base[cleared] * self.level + bonus
            self.lines += cleared
            self.level = self.lines // 10 + 1
        else:
            self.combo = 0

    # ── DESENHO ──────────────────────────────────────────────

    def draw(self):
        self.canvas.delete('all')
        self._draw_grid()
        self._draw_board()
        self._draw_ghost()
        self._draw_piece()
        if self.game_over:
            self._draw_game_over()
        elif self.paused:
            self._draw_pause()
        self._draw_panel()

    def _draw_grid(self):
        for c in range(COLS):
            for r in range(ROWS):
                x0, y0 = c*CELL, r*CELL
                self.canvas.create_rectangle(
                    x0+1, y0+1, x0+CELL-1, y0+CELL-1,
                    fill=COLORS['grid'], outline='', width=0
                )

    def _draw_board(self):
        for r in range(ROWS):
            for c in range(COLS):
                color = self.board[r][c]
                if color:
                    self._draw_cell(c, r, color)

    def _draw_ghost(self):
        gy = self.ghost_y()
        if gy == self.current.y:
            return
        for cx, cy in self.current.cells(y=gy):
            if cy >= 0:
                x0, y0 = cx*CELL, cy*CELL
                self.canvas.create_rectangle(
                    x0+2, y0+2, x0+CELL-2, y0+CELL-2,
                    fill='', outline=self.current.color(), width=1,
                    dash=(4, 3)
                )

    def _draw_piece(self):
        for cx, cy in self.current.cells():
            if cy >= 0:
                self._draw_cell(cx, cy, self.current.color())

    def _draw_cell(self, c, r, color):
        x0, y0 = c*CELL, r*CELL
        pad = 1
        # Corpo
        self.canvas.create_rectangle(
            x0+pad, y0+pad, x0+CELL-pad, y0+CELL-pad,
            fill=color, outline='', width=0
        )
        # Brilho superior
        self.canvas.create_rectangle(
            x0+pad, y0+pad, x0+CELL-pad, y0+pad+4,
            fill='white', stipple='gray50', outline='', width=0
        )
        # Sombra inferior
        self.canvas.create_rectangle(
            x0+pad, y0+CELL-pad-3, x0+CELL-pad, y0+CELL-pad,
            fill='black', stipple='gray50', outline='', width=0
        )

    def _draw_game_over(self):
        self.canvas.create_rectangle(0, HEIGHT//2-60, WIDTH, HEIGHT//2+60,
                                     fill='#000000CC', outline='')
        self.canvas.create_text(WIDTH//2, HEIGHT//2-20,
                                text='GAME OVER', font=('Courier', 22, 'bold'),
                                fill='#FF2D55')
        self.canvas.create_text(WIDTH//2, HEIGHT//2+20,
                                text=f'Score: {self.score}', font=('Courier', 14),
                                fill=COLORS['text'])
        self.canvas.create_text(WIDTH//2, HEIGHT//2+45,
                                text='[R] Reiniciar', font=('Courier', 11),
                                fill=COLORS['accent'])

    def _draw_pause(self):
        self.canvas.create_rectangle(0, HEIGHT//2-40, WIDTH, HEIGHT//2+40,
                                     fill='#000000CC', outline='')
        self.canvas.create_text(WIDTH//2, HEIGHT//2,
                                text='PAUSADO', font=('Courier', 22, 'bold'),
                                fill=COLORS['accent'])

    def _draw_panel(self):
        self.panel.delete('all')
        pw = PANEL_W
        self.panel.create_text(pw//2, 18, text='TETRIS', font=('Courier', 15, 'bold'),
                               fill=COLORS['accent'])
        self.panel.create_line(10, 32, pw-10, 32, fill='#2A2A4A')

        # Pontuação
        self._panel_label(50, 'SCORE', str(self.score))
        self._panel_label(100, 'NÍVEL', str(self.level))
        self._panel_label(148, 'LINHAS', str(self.lines))

        self.panel.create_line(10, 175, pw-10, 175, fill='#2A2A4A')

        # Próxima peça
        self.panel.create_text(pw//2, 192, text='PRÓXIMA', font=('Courier', 10, 'bold'),
                               fill='#8888AA')
        self._draw_mini(self.next_piece, 210)

        self.panel.create_line(10, 275, pw-10, 275, fill='#2A2A4A')

        # Hold
        self.panel.create_text(pw//2, 292, text='HOLD', font=('Courier', 10, 'bold'),
                               fill='#8888AA' if not self.hold_used else '#444466')
        if self.hold:
            p = Piece(self.hold.shape)
            self._draw_mini(p, 310, faded=self.hold_used)

        # Controles
        self.panel.create_line(10, HEIGHT-160, pw-10, HEIGHT-160, fill='#2A2A4A')
        controls = [
            ('←→', 'Mover'),
            ('↑', 'Girar'),
            ('↓', 'Descer'),
            ('ESPAÇO', 'Drop'),
            ('C', 'Hold'),
            ('P', 'Pausa'),
            ('R', 'Reset'),
        ]
        for i, (key, desc) in enumerate(controls):
            y = HEIGHT - 148 + i * 19
            self.panel.create_text(28, y, text=key, font=('Courier', 9, 'bold'),
                                   fill=COLORS['accent'], anchor='e')
            self.panel.create_text(33, y, text=desc, font=('Courier', 9),
                                   fill=COLORS['text'], anchor='w')

    def _panel_label(self, y, label, value):
        pw = PANEL_W
        self.panel.create_text(pw//2, y, text=label, font=('Courier', 9),
                               fill='#8888AA')
        self.panel.create_text(pw//2, y+20, text=value, font=('Courier', 16, 'bold'),
                               fill=COLORS['text'])

    def _draw_mini(self, piece, y_offset, faded=False):
        cs = 18
        cells = piece.cells(x=0, y=0)
        min_x = min(c[0] for c in cells)
        min_y = min(c[1] for c in cells)
        max_x = max(c[0] for c in cells)
        max_y = max(c[1] for c in cells)
        span_x = (max_x - min_x + 1) * cs
        span_y = (max_y - min_y + 1) * cs
        ox = (PANEL_W - span_x) // 2
        oy = y_offset

        color = piece.color() if not faded else '#333355'
        for cx, cy in cells:
            x0 = ox + (cx - min_x) * cs
            y0 = oy + (cy - min_y) * cs
            self.panel.create_rectangle(
                x0+1, y0+1, x0+cs-1, y0+cs-1,
                fill=color, outline=''
            )

    # ── TECLADO ──────────────────────────────────────────────

    def on_key(self, event):
        k = event.keysym.lower()
        if k == 'r':
            self.reset()
            return
        if self.game_over:
            return
        if k == 'p':
            self.paused = not self.paused
            self.draw()
            return
        if self.paused:
            return

        actions = {
            'left':  lambda: self.move(-1, 0),
            'right': lambda: self.move(1, 0),
            'down':  lambda: self.soft_drop(),
            'up':    lambda: self.rotate(1),
            'z':     lambda: self.rotate(-1),
            'space': lambda: self.hard_drop(),
            'c':     lambda: self.hold_piece(),
        }
        action = actions.get(k)
        if action:
            action()


def main():
    root = tk.Tk()
    game = Tetris(root)
    root.mainloop()


if __name__ == '__main__':
    main()