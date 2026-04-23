import tkinter as tk
import math
import random

# ═══════════════════════════════════════════════════════════════
#  CONFIGURAÇÕES
# ═══════════════════════════════════════════════════════════════
COLS, ROWS = 7, 6
CELL       = 90
RADIUS     = 36
PAD        = (CELL - 2 * RADIUS) // 2

WIDTH      = COLS * CELL
HEIGHT     = ROWS * CELL + 110   # +110: topo (preview) + base (HUD)

BG         = "#1a1a2e"
BOARD_BG   = "#16213e"
BOARD_FG   = "#0f3460"
C_EMPTY    = "#0a0a1a"
C_P1       = "#e94560"   # vermelho — jogador
C_P2       = "#f5a623"   # amarelo — IA
C_WIN      = "#ffffff"
C_TEXT     = "#eaeaea"
C_GOLD     = "#f9ca24"
C_BTN_1    = "#e94560"
C_BTN_2    = "#27ae60"
C_BTN_3    = "#7f8c8d"

EMPTY, P1, P2 = 0, 1, 2
AI_DEPTH = 6   # profundidade do minimax (≥5 = desafiador)


# ═══════════════════════════════════════════════════════════════
#  LÓGICA DO TABULEIRO
# ═══════════════════════════════════════════════════════════════
def make_board():
    return [[EMPTY]*COLS for _ in range(ROWS)]

def copy_board(b):
    return [row[:] for row in b]

def valid_cols(b):
    return [c for c in range(COLS) if b[0][c] == EMPTY]

def drop(b, col, player):
    for r in range(ROWS-1, -1, -1):
        if b[r][col] == EMPTY:
            b[r][col] = player
            return r
    return -1

def check_win(b, player):
    # horizontal
    for r in range(ROWS):
        for c in range(COLS-3):
            if all(b[r][c+i] == player for i in range(4)):
                return [(r,c+i) for i in range(4)]
    # vertical
    for r in range(ROWS-3):
        for c in range(COLS):
            if all(b[r+i][c] == player for i in range(4)):
                return [(r+i,c) for i in range(4)]
    # diagonal ↘
    for r in range(ROWS-3):
        for c in range(COLS-3):
            if all(b[r+i][c+i] == player for i in range(4)):
                return [(r+i,c+i) for i in range(4)]
    # diagonal ↙
    for r in range(ROWS-3):
        for c in range(3, COLS):
            if all(b[r+i][c-i] == player for i in range(4)):
                return [(r+i,c-i) for i in range(4)]
    return []

def is_full(b):
    return all(b[0][c] != EMPTY for c in range(COLS))

def score_window(window, player):
    opp = P1 if player == P2 else P2
    p_count = window.count(player)
    e_count = window.count(EMPTY)
    o_count = window.count(opp)
    if p_count == 4:             return 100
    if p_count == 3 and e_count == 1: return 5
    if p_count == 2 and e_count == 2: return 2
    if o_count == 3 and e_count == 1: return -4
    return 0

def heuristic(b, player):
    score = 0
    # centro vale mais
    center = [b[r][COLS//2] for r in range(ROWS)]
    score += center.count(player) * 3

    for r in range(ROWS):
        for c in range(COLS-3):
            score += score_window([b[r][c+i] for i in range(4)], player)
    for r in range(ROWS-3):
        for c in range(COLS):
            score += score_window([b[r+i][c] for i in range(4)], player)
    for r in range(ROWS-3):
        for c in range(COLS-3):
            score += score_window([b[r+i][c+i] for i in range(4)], player)
    for r in range(ROWS-3):
        for c in range(3, COLS):
            score += score_window([b[r+i][c-i] for i in range(4)], player)
    return score

def minimax(b, depth, alpha, beta, maximizing):
    wins_p2 = check_win(b, P2)
    wins_p1 = check_win(b, P1)
    if wins_p2: return None, 100000 + depth
    if wins_p1: return None, -(100000 + depth)
    if is_full(b) or depth == 0:
        return None, heuristic(b, P2)

    cols = valid_cols(b)
    # prefere centro
    cols.sort(key=lambda c: abs(c - COLS//2))

    if maximizing:
        best_score = -math.inf
        best_col   = cols[0]
        for c in cols:
            nb = copy_board(b)
            drop(nb, c, P2)
            _, sc = minimax(nb, depth-1, alpha, beta, False)
            if sc > best_score:
                best_score, best_col = sc, c
            alpha = max(alpha, best_score)
            if alpha >= beta: break
        return best_col, best_score
    else:
        best_score = math.inf
        best_col   = cols[0]
        for c in cols:
            nb = copy_board(b)
            drop(nb, c, P1)
            _, sc = minimax(nb, depth-1, alpha, beta, True)
            if sc < best_score:
                best_score, best_col = sc, c
            beta = min(beta, best_score)
            if alpha >= beta: break
        return best_col, best_score


# ═══════════════════════════════════════════════════════════════
#  INTERFACE
# ═══════════════════════════════════════════════════════════════
class ConnectFour:
    def __init__(self, root):
        self.root = root
        self.root.title("🔵 Connect Four")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.cv = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                            bg=BG, highlightthickness=0)
        self.cv.pack()

        self.board     = make_board()
        self.turn      = P1          # P1 = humano, P2 = IA
        self.over      = False
        self.win_cells = []
        self.hover_col = -1
        self.scores    = {P1: 0, P2: 0}
        self.ai_mode   = True        # True = vs IA, False = 2 jogadores

        self.cv.bind("<Motion>",    self._mouse_move)
        self.cv.bind("<Button-1>",  self._mouse_click)
        self.root.bind("<KeyPress>", self._key)

        self._draw()

    # ── coordenadas ───────────────────────────────────────────
    def _cx(self, col): return col * CELL + CELL // 2
    def _cy(self, row): return 90 + row * CELL + CELL // 2   # 90 = topo preview

    def _col_from_x(self, x):
        c = x // CELL
        return c if 0 <= c < COLS else -1

    # ── eventos ───────────────────────────────────────────────
    def _mouse_move(self, e):
        if self.over or (self.ai_mode and self.turn == P2): return
        c = self._col_from_x(e.x)
        if c != self.hover_col:
            self.hover_col = c
            self._draw()

    def _mouse_click(self, e):
        if self.over or (self.ai_mode and self.turn == P2): return
        c = self._col_from_x(e.x)
        if c < 0 or self.board[0][c] != EMPTY: return
        self._play(c)

    def _key(self, e):
        k = e.keysym.lower()
        if k == "r":
            self._reset_board()
        elif k == "n":
            self._new_game()
        elif k in [str(i) for i in range(1, COLS+1)]:
            c = int(k) - 1
            if not self.over and not (self.ai_mode and self.turn == P2):
                if 0 <= c < COLS and self.board[0][c] == EMPTY:
                    self._play(c)

    # ── jogada ────────────────────────────────────────────────
    def _play(self, col):
        if self.over: return
        player = self.turn
        drop(self.board, col, player)
        self._draw()

        win = check_win(self.board, player)
        if win:
            self.win_cells = win
            self.scores[player] += 1
            self.over = True
            self._draw()
            return

        if is_full(self.board):
            self.over = True
            self._draw()
            return

        self.turn = P2 if player == P1 else P1

        if self.ai_mode and self.turn == P2:
            self.root.after(200, self._ai_move)
        else:
            self._draw()

    def _ai_move(self):
        if self.over: return
        col, _ = minimax(self.board, AI_DEPTH, -math.inf, math.inf, True)
        if col is None:
            cols = valid_cols(self.board)
            col  = random.choice(cols) if cols else 0
        self._play(col)

    def _reset_board(self):
        self.board     = make_board()
        self.turn      = P1
        self.over      = False
        self.win_cells = []
        self.hover_col = -1
        self._draw()

    def _new_game(self):
        self.scores    = {P1: 0, P2: 0}
        self._reset_board()

    # ═══════════════════════════════════════════════════════════
    #  DESENHO
    # ═══════════════════════════════════════════════════════════
    def _draw(self):
        self.cv.delete("all")
        self._draw_bg()
        self._draw_preview()
        self._draw_board()
        self._draw_pieces()
        self._draw_hud()
        if self.over:
            self._draw_overlay()

    def _draw_bg(self):
        self.cv.create_rectangle(0, 0, WIDTH, HEIGHT, fill=BG, outline="")

    def _draw_preview(self):
        """Disco flutuante mostrando onde vai cair."""
        if self.over: return
        if self.hover_col < 0: return
        if self.board[0][self.hover_col] != EMPTY: return
        col   = C_P1 if self.turn == P1 else C_P2
        cx    = self._cx(self.hover_col)
        cy    = 45
        r     = RADIUS - 4
        # brilho
        self.cv.create_oval(cx-r-3, cy-r-3, cx+r+3, cy+r+3,
                            fill=col, outline="")
        self.cv.create_oval(cx-r, cy-r, cx+r, cy+r,
                            fill=col, outline="")
        # reflexo
        self.cv.create_oval(cx-r+6, cy-r+4, cx-r+16, cy-r+12,
                            fill=self._lighten(col, 60), outline="")

    def _draw_board(self):
        # fundo do tabuleiro
        bx1, by1 = 0, 90
        bx2, by2 = WIDTH, 90 + ROWS * CELL
        self.cv.create_rectangle(bx1, by1, bx2, by2,
                                 fill=BOARD_BG, outline="")
        # buracos vazios
        for r in range(ROWS):
            for c in range(COLS):
                cx = self._cx(c)
                cy = self._cy(r)
                # sombra interna
                self.cv.create_oval(cx-RADIUS-2, cy-RADIUS-2,
                                    cx+RADIUS+2, cy+RADIUS+2,
                                    fill=BOARD_FG, outline="")
                self.cv.create_oval(cx-RADIUS, cy-RADIUS,
                                    cx+RADIUS, cy+RADIUS,
                                    fill=C_EMPTY, outline="")

    def _draw_pieces(self):
        win_set = set(map(tuple, self.win_cells))
        for r in range(ROWS):
            for c in range(COLS):
                p = self.board[r][c]
                if p == EMPTY: continue
                cx = self._cx(c)
                cy = self._cy(r)
                col = C_P1 if p == P1 else C_P2

                is_win = (r, c) in win_set
                if is_win:
                    # halo pulsante (simulado com anéis)
                    self.cv.create_oval(cx-RADIUS-6, cy-RADIUS-6,
                                        cx+RADIUS+6, cy+RADIUS+6,
                                        fill=col, outline=C_WIN, width=3)
                else:
                    self.cv.create_oval(cx-RADIUS, cy-RADIUS,
                                        cx+RADIUS, cy+RADIUS,
                                        fill=col, outline="")

                # reflexo
                self.cv.create_oval(cx-RADIUS+6, cy-RADIUS+5,
                                    cx-RADIUS+18, cy-RADIUS+14,
                                    fill=self._lighten(col, 70), outline="")

    def _draw_hud(self):
        base = 90 + ROWS * CELL
        self.cv.create_rectangle(0, base, WIDTH, HEIGHT,
                                 fill=BG, outline="")
        # linha separadora
        self.cv.create_line(0, base, WIDTH, base, fill="#2a2a4a", width=2)

        # Jogador 1
        self.cv.create_oval(24, base+18, 24+22, base+40,
                            fill=C_P1, outline="")
        lbl1 = "Você" if self.ai_mode else "P1"
        self.cv.create_text(54, base+29, text=f"{lbl1}: {self.scores[P1]}",
                            font=("Courier",13,"bold"), fill=C_P1, anchor="w")

        # Jogador 2
        self.cv.create_oval(WIDTH//2+20, base+18,
                            WIDTH//2+42, base+40, fill=C_P2, outline="")
        lbl2 = "IA" if self.ai_mode else "P2"
        self.cv.create_text(WIDTH//2+50, base+29,
                            text=f"{lbl2}: {self.scores[P2]}",
                            font=("Courier",13,"bold"), fill=C_P2, anchor="w")

        # Turno atual
        if not self.over:
            col  = C_P1 if self.turn == P1 else C_P2
            name = ("Sua vez" if self.ai_mode and self.turn == P1
                    else "IA pensando..." if self.ai_mode and self.turn == P2
                    else f"Vez do P{self.turn}")
            self.cv.create_text(WIDTH//2, base+55,
                                text=name,
                                font=("Courier",12,"bold"), fill=col)

        # Atalhos
        self.cv.create_text(WIDTH//2, base+78,
                            text="R  reiniciar   |   N  nova partida   |   1-7  jogar",
                            font=("Courier",9), fill="#555577")

    def _draw_overlay(self):
        win_p1 = check_win(self.board, P1)
        win_p2 = check_win(self.board, P2)
        draw   = is_full(self.board) and not win_p1 and not win_p2

        if draw:
            msg, col = "EMPATE!", "#95a5a6"
        elif win_p1:
            msg = "VOCÊ VENCEU!" if self.ai_mode else "P1 VENCEU!"
            col = C_P1
        else:
            msg = "IA VENCEU!" if self.ai_mode else "P2 VENCEU!"
            col = C_P2

        cx = WIDTH // 2
        cy = 90 + ROWS * CELL // 2

        # fundo semiopaco (simulado com retângulo escuro)
        self.cv.create_rectangle(cx-200, cy-40, cx+200, cy+40,
                                 fill="#0a0a1a", outline=col, width=2)
        self.cv.create_text(cx, cy-8, text=msg,
                            font=("Courier", 26, "bold"), fill=col)
        self.cv.create_text(cx, cy+22,
                            text="R  para jogar novamente",
                            font=("Courier", 11), fill=C_TEXT)

    # ── utilitário de cor ─────────────────────────────────────
    def _lighten(self, hex_color, amount=40):
        try:
            r = min(255, int(hex_color[1:3], 16) + amount)
            g = min(255, int(hex_color[3:5], 16) + amount)
            b = min(255, int(hex_color[5:7], 16) + amount)
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return hex_color


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    ConnectFour(root)
    root.mainloop()