import tkinter as tk
from tkinter import messagebox
import copy

PIECES = {
    'wK': '♔', 'wQ': '♕', 'wR': '♖', 'wB': '♗', 'wN': '♘', 'wP': '♙',
    'bK': '♚', 'bQ': '♛', 'bR': '♜', 'bB': '♝', 'bN': '♞', 'bP': '♟',
}

LIGHT = '#F0D9B5'
DARK  = '#B58863'
SEL   = '#F6F669'
LEGAL = '#CDD16E'
LEGAL_DARK = '#AAAA44'
CHECK = '#FF6B6B'

def init_board():
    return [
        ['bR','bN','bB','bQ','bK','bB','bN','bR'],
        ['bP','bP','bP','bP','bP','bP','bP','bP'],
        [None]*8, [None]*8, [None]*8, [None]*8,
        ['wP','wP','wP','wP','wP','wP','wP','wP'],
        ['wR','wN','wB','wQ','wK','wB','wN','wR'],
    ]

def color(p): return p[0] if p else None
def ptype(p): return p[1] if p else None
def opp(c): return 'b' if c == 'w' else 'w'
def in_bounds(r, c): return 0 <= r < 8 and 0 <= c < 8

def piece_moves(board, r, c, ep, castle_rights, check_castle=True):
    p = board[r][c]
    if not p: return []
    col, t = color(p), ptype(p)
    moves = []
    def add(nr, nc):
        if in_bounds(nr, nc): moves.append((nr, nc))

    if t == 'P':
        d = -1 if col == 'w' else 1
        start = 6 if col == 'w' else 1
        if in_bounds(r+d, c) and not board[r+d][c]:
            add(r+d, c)
            if r == start and not board[r+2*d][c]:
                add(r+2*d, c)
        for dc in (-1, 1):
            if in_bounds(r+d, c+dc):
                if board[r+d][c+dc] and color(board[r+d][c+dc]) == opp(col):
                    add(r+d, c+dc)
                if ep and (r+d, c+dc) == ep:
                    add(r+d, c+dc)
    elif t == 'N':
        for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            if in_bounds(r+dr, c+dc) and color(board[r+dr][c+dc]) != col:
                add(r+dr, c+dc)
    elif t == 'K':
        for dr, dc in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
            if in_bounds(r+dr, c+dc) and color(board[r+dr][c+dc]) != col:
                add(r+dr, c+dc)
        if check_castle and castle_rights:
            row = 7 if col == 'w' else 0
            cr = castle_rights[col]
            if cr['K'] and not board[row][5] and not board[row][6]:
                if not is_attacked(board,row,4,opp(col)) and not is_attacked(board,row,5,opp(col)) and not is_attacked(board,row,6,opp(col)):
                    add(row, 6)
            if cr['Q'] and not board[row][3] and not board[row][2] and not board[row][1]:
                if not is_attacked(board,row,4,opp(col)) and not is_attacked(board,row,3,opp(col)) and not is_attacked(board,row,2,opp(col)):
                    add(row, 2)
    else:
        if t == 'R':    dirs = [(0,1),(0,-1),(1,0),(-1,0)]
        elif t == 'B':  dirs = [(1,1),(1,-1),(-1,1),(-1,-1)]
        else:            dirs = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
        for dr, dc in dirs:
            nr, nc = r+dr, c+dc
            while in_bounds(nr, nc):
                if color(board[nr][nc]) == col: break
                add(nr, nc)
                if board[nr][nc]: break
                nr += dr; nc += dc
    return moves

def is_attacked(board, r, c, by_color):
    for rr in range(8):
        for cc in range(8):
            if color(board[rr][cc]) == by_color:
                if (r, c) in piece_moves(board, rr, cc, None, None, False):
                    return True
    return False

def find_king(board, col):
    for r in range(8):
        for c in range(8):
            if board[r][c] == col + 'K':
                return (r, c)

def apply_move(board, fr, fc, tr, tc, castle_rights, ep, promo=None):
    nb = copy.deepcopy(board)
    new_cr = copy.deepcopy(castle_rights)
    p = nb[fr][fc]
    col, t = color(p), ptype(p)
    new_ep = None
    if t == 'P' and abs(tr - fr) == 2:
        new_ep = ((fr + tr) // 2, fc)
    if t == 'P' and ep and (tr, tc) == ep:
        nb[fr][tc] = None
    if t == 'K':
        new_cr[col]['K'] = False
        new_cr[col]['Q'] = False
        if abs(tc - fc) == 2:
            row = fr
            if tc == 6: nb[row][5] = nb[row][7]; nb[row][7] = None
            else:       nb[row][3] = nb[row][0]; nb[row][0] = None
    if t == 'R':
        if fc == 7: new_cr[col]['K'] = False
        if fc == 0: new_cr[col]['Q'] = False
    nb[tr][tc] = col + promo if promo else p
    nb[fr][fc] = None
    return nb, new_ep, new_cr

def legal_moves_for(board, r, c, ep, castle_rights):
    p = board[r][c]
    if not p: return []
    col = color(p)
    raw = piece_moves(board, r, c, ep, castle_rights, True)
    result = []
    for (tr, tc) in raw:
        nb, _, _ = apply_move(board, r, c, tr, tc, castle_rights, ep)
        kr, kc = find_king(nb, col)
        if not is_attacked(nb, kr, kc, opp(col)):
            result.append((tr, tc))
    return result

def all_legal(board, col, ep, castle_rights):
    moves = []
    for r in range(8):
        for c in range(8):
            if color(board[r][c]) == col:
                for tr, tc in legal_moves_for(board, r, c, ep, castle_rights):
                    moves.append((r, c, tr, tc))
    return moves

def in_check(board, col):
    kr, kc = find_king(board, col)
    return is_attacked(board, kr, kc, opp(col))


class ChessApp:
    SQ = 72

    def __init__(self, root):
        self.root = root
        self.root.title('Xadrez')
        self.root.resizable(False, False)
        self.flipped = False
        self._build_ui()
        self.new_game()

    def _build_ui(self):
        top = tk.Frame(self.root, bg='#2C2C2A', pady=6)
        top.pack(fill='x')
        self.status_var = tk.StringVar(value='')
        tk.Label(top, textvariable=self.status_var, bg='#2C2C2A', fg='#F0D9B5',
                 font=('Helvetica', 13)).pack()

        board_frame = tk.Frame(self.root, bg='#2C2C2A')
        board_frame.pack(padx=12, pady=(4, 4))

        self.canvas = tk.Canvas(board_frame, width=self.SQ*8, height=self.SQ*8,
                                highlightthickness=0, bd=0)
        self.canvas.pack()
        self.canvas.bind('<Button-1>', self.on_click)

        btn_frame = tk.Frame(self.root, bg='#2C2C2A', pady=6)
        btn_frame.pack(fill='x')
        style = dict(bg='#3C3C3A', fg='#F0D9B5', activebackground='#555',
                     activeforeground='white', relief='flat', padx=14, pady=5,
                     font=('Helvetica', 11), cursor='hand2')
        tk.Button(btn_frame, text='Nova partida', command=self.new_game, **style).pack(side='left', padx=(12,4))
        tk.Button(btn_frame, text='Virar tabuleiro', command=self.flip, **style).pack(side='left', padx=4)

    def new_game(self):
        self.board = init_board()
        self.turn = 'w'
        self.ep = None
        self.castle_rights = {'w': {'K': True, 'Q': True}, 'b': {'K': True, 'Q': True}}
        self.selected = None
        self.legal = []
        self.game_over = False
        self.status_var.set('Turno das Brancas')
        self.draw()

    def flip(self):
        self.flipped = not self.flipped
        self.draw()

    def sq_to_rc(self, sq_x, sq_y):
        c = sq_x if not self.flipped else 7 - sq_x
        r = sq_y if not self.flipped else 7 - sq_y
        return r, c

    def rc_to_xy(self, r, c):
        x = c if not self.flipped else 7 - c
        y = r if not self.flipped else 7 - r
        return x, y

    def draw(self):
        S = self.SQ
        c = self.canvas
        c.delete('all')
        names = 'abcdefgh'
        check_pos = find_king(self.board, self.turn) if in_check(self.board, self.turn) else None

        for row in range(8):
            for col in range(8):
                r, brd_c = self.sq_to_rc(col, row)
                x1, y1 = col * S, row * S
                x2, y2 = x1 + S, y1 + S

                is_light = (r + brd_c) % 2 == 0
                base = LIGHT if is_light else DARK
                fill = base

                if self.selected and self.selected == (r, brd_c):
                    fill = SEL
                elif (r, brd_c) in self.legal:
                    fill = LEGAL if is_light else LEGAL_DARK
                elif check_pos and (r, brd_c) == check_pos:
                    fill = CHECK

                c.create_rectangle(x1, y1, x2, y2, fill=fill, outline='')

                # dot for legal empty squares
                if (r, brd_c) in self.legal and not self.board[r][brd_c]:
                    cx, cy = x1 + S//2, y1 + S//2
                    dot_color = '#888844' if is_light else '#666622'
                    c.create_oval(cx-8, cy-8, cx+8, cy+8, fill=dot_color, outline='')

                p = self.board[r][brd_c]
                if p:
                    piece_color = '#FFFFF0' if p[0] == 'w' else '#1A1A1A'
                    c.create_text(x1+S//2, y1+S//2, text=PIECES[p],
                                  font=('Segoe UI Emoji', int(S*0.55)), fill=piece_color)

        # coordinates
        for i in range(8):
            xi, yi = self.rc_to_xy(0, i)
            c.create_text(xi*S + 4, 8*S - 6, text=names[i],
                          font=('Helvetica', 9), fill=DARK if i%2==0 else LIGHT, anchor='w')
        for i in range(8):
            xi, yi = self.rc_to_xy(i, 0)
            num = str(8 - i) if not self.flipped else str(i + 1)
            c.create_text(2, yi*S + 6, text=num,
                          font=('Helvetica', 9), fill=LIGHT if i%2==0 else DARK, anchor='nw')

    def on_click(self, event):
        if self.game_over: return
        S = self.SQ
        col_x = event.x // S
        row_y = event.y // S
        if not (0 <= col_x < 8 and 0 <= row_y < 8): return
        r, c = self.sq_to_rc(col_x, row_y)

        if self.selected:
            if (r, c) in self.legal:
                self.do_move(self.selected[0], self.selected[1], r, c)
                return
        if self.board[r][c] and color(self.board[r][c]) == self.turn:
            self.selected = (r, c)
            self.legal = legal_moves_for(self.board, r, c, self.ep, self.castle_rights)
        else:
            self.selected = None
            self.legal = []
        self.draw()

    def do_move(self, fr, fc, tr, tc, promo=None):
        p = self.board[fr][fc]
        col = color(p)
        is_promo_row = (col == 'w' and tr == 0) or (col == 'b' and tr == 7)
        if ptype(p) == 'P' and is_promo_row and not promo:
            self.ask_promotion(col, lambda ch: self.do_move(fr, fc, tr, tc, ch))
            return

        self.board, self.ep, self.castle_rights = apply_move(
            self.board, fr, fc, tr, tc, self.castle_rights, self.ep, promo)
        self.turn = opp(self.turn)
        self.selected = None
        self.legal = []

        avail = all_legal(self.board, self.turn, self.ep, self.castle_rights)
        names = {'w': 'Brancas', 'b': 'Pretas'}
        self.draw()

        if not avail:
            self.game_over = True
            if in_check(self.board, self.turn):
                winner = names[opp(self.turn)]
                self.status_var.set(f'Xeque-mate! {winner} vencem!')
                messagebox.showinfo('Fim de jogo', f'Xeque-mate!\n{winner} vencem!')
            else:
                self.status_var.set('Empate por afogamento!')
                messagebox.showinfo('Fim de jogo', 'Empate por afogamento!')
        elif in_check(self.board, self.turn):
            self.status_var.set(f'Xeque! Turno das {names[self.turn]}')
        else:
            self.status_var.set(f'Turno das {names[self.turn]}')

    def ask_promotion(self, col, callback):
        win = tk.Toplevel(self.root)
        win.title('Promoção do peão')
        win.resizable(False, False)
        win.grab_set()
        tk.Label(win, text='Escolha a peça:', font=('Helvetica', 12), pady=8).pack()
        frame = tk.Frame(win)
        frame.pack(padx=16, pady=(0, 12))
        for t in ['Q', 'R', 'B', 'N']:
            sym = PIECES[col + t]
            def make_cb(choice=t):
                win.destroy()
                callback(choice)
            tk.Button(frame, text=sym, font=('Segoe UI Emoji', 32),
                      width=2, relief='flat', bg='#F0D9B5',
                      activebackground='#CDD16E', cursor='hand2',
                      command=make_cb).pack(side='left', padx=4)
        win.protocol('WM_DELETE_WINDOW', lambda: None)
        self.root.wait_window(win)


if __name__ == '__main__':
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()