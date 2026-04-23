import tkinter as tk
import random
import time

# ── Configurações ──────────────────────────────────────────────
CELL   = 52
COLS   = 13
ROWS   = 13
WIDTH  = COLS * CELL
HEIGHT = ROWS * CELL + 60   # +60 HUD

FPS      = 60
FRAME_MS = 1000 // FPS

C_BG        = "#0d0d1a"
C_GRASS     = "#1a5c1a"
C_ROAD      = "#2a2a2a"
C_WATER     = "#0a3d62"
C_WATER2    = "#0c4a75"
C_HOME_OPEN = "#0a3d62"
C_HOME_FILL = "#0d5c0d"
C_SCORE     = "#f9ca24"
C_TIME_OK   = "#6ab04c"
C_TIME_WARN = "#f0932b"
C_TIME_BAD  = "#eb4d4b"
C_TEXT      = "#ffffff"

ROAD_ROWS  = {7, 8, 9, 10, 11}
RIVER_ROWS = {1, 2, 3, 4, 5}
HOME_ROW   = 0
HOME_COLS  = [1, 3, 5, 7, 9, 11]
TIME_LIMIT = 30.0

LANES = [
    (11, 130,  1, "car",    "#eb4d4b", 2, 3),
    (10, 104, -1, "car",    "#f9ca24", 2, 4),
    ( 9, 156,  1, "car",    "#6c5ce7", 3, 2),
    ( 8,  94, -1, "truck",  "#fd9644", 3, 3),
    ( 7, 146,  1, "car",    "#00b894", 2, 3),
    ( 5,  78,  1, "log",    "#8B5E3C", 3, 3),
    ( 4, 104, -1, "turtle", "#2ecc71", 2, 4),
    ( 3,  62,  1, "log",    "#7B4F2E", 4, 2),
    ( 2, 130, -1, "turtle", "#27ae60", 2, 3),
    ( 1,  94,  1, "log",    "#6B3F1E", 3, 3),
]


def row_y(r):
    return 60 + r * CELL


def draw_frog(canvas, cx, cy, dead=False):
    color = "#00ff7f" if not dead else "#888888"
    dark  = "#009955" if not dead else "#555555"
    r = 18
    canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=color, outline=dark, width=2)
    for ox in (-9, 9):
        canvas.create_oval(cx+ox-5, cy-r-2, cx+ox+5, cy-r+8,
                           fill="white", outline=dark)
        canvas.create_oval(cx+ox-2, cy-r+1, cx+ox+2, cy-r+5,
                           fill="black", outline="")
    for ox, oa in ((-r, -1), (r, 1)):
        canvas.create_line(cx+ox, cy+8, cx+ox+oa*14, cy+r+8, fill=dark, width=4)
        canvas.create_line(cx+ox, cy-4, cx+ox+oa*12, cy-14, fill=dark, width=3)


def draw_car(canvas, x, y, w, color):
    h = CELL - 8
    x1, y1, x2, y2 = x+2, y+4, x+w-2, y+h
    canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
    canvas.create_rectangle(x1+6, y1-4, x2-6, y1+8, fill=color, outline="")
    for fx in (x1+3, x2-8):
        canvas.create_rectangle(fx, y2-7, fx+5, y2-2, fill="#ffffaa", outline="")
    for wx in (x1+4, x2-9):
        canvas.create_oval(wx, y2-2, wx+8, y2+4, fill="#111", outline="#555")


def draw_truck(canvas, x, y, w, color):
    h = CELL - 6
    x1, y1, x2, y2 = x+1, y+3, x+w-1, y+h
    cab = 26
    canvas.create_rectangle(x1, y1+6, x2-cab, y2, fill=color, outline="")
    canvas.create_rectangle(x2-cab, y1, x2, y2, fill=color, outline="")
    canvas.create_rectangle(x2-cab+3, y1+3, x2-3, y1+12, fill="#aaddff", outline="")
    for wx in (x1+4, x2-32, x2-12):
        canvas.create_oval(wx, y2-2, wx+10, y2+5, fill="#111", outline="#555")


def draw_log(canvas, x, y, w):
    x1, y1, x2, y2 = x, y+5, x+w, y+CELL-10
    canvas.create_rectangle(x1, y1, x2, y2, fill="#8B5E3C", outline="#5a3a1a", width=2)
    for lx in range(x1+14, x2-4, 22):
        canvas.create_line(lx, y1+2, lx, y2-2, fill="#5a3a1a", width=1)
    canvas.create_oval(x1, y1, x1+14, y2, fill="#7a5230", outline="#5a3a1a")
    canvas.create_oval(x2-14, y1, x2, y2, fill="#7a5230", outline="#5a3a1a")


def draw_turtle(canvas, x, y, w):
    count = max(1, w // CELL)
    for i in range(count):
        cx = x + i*CELL + CELL//2
        cy = y + CELL//2
        tw = CELL - 10
        canvas.create_oval(cx-tw//2, cy-10, cx+tw//2, cy+10,
                           fill="#27ae60", outline="#1e8449", width=2)
        canvas.create_oval(cx-6, cy-5, cx+6, cy+5, fill="#145a32", outline="")
        canvas.create_oval(cx-5, cy-15, cx+5, cy-5, fill="#2ecc71", outline="#1e8449")
        for px_, py_ in [(-tw//2-3, -4), (tw//2+3, -4),
                          (-tw//2-3,  6), (tw//2+3,  6)]:
            canvas.create_oval(cx+px_-3, cy+py_-3, cx+px_+3, cy+py_+3,
                               fill="#2ecc71", outline="")


class LaneObj:
    def __init__(self, row, x, speed, direction, otype, color, w_cells):
        self.row = row
        self.x   = float(x)
        self.spd = float(speed)
        self.dir = direction
        self.typ = otype
        self.col = color
        self.w   = w_cells * CELL

    def update(self, dt):
        self.x += self.spd * self.dir * dt
        if self.dir == 1 and self.x > WIDTH + 40:
            self.x = -self.w - 10
        elif self.dir == -1 and self.x < -self.w - 40:
            self.x = WIDTH + 10

    def left(self):  return self.x
    def right(self): return self.x + self.w
    def top(self):   return float(row_y(self.row))
    def bot(self):   return self.top() + CELL

    def draw(self, canvas):
        x, y = int(self.x), row_y(self.row)
        if self.typ == "car":      draw_car(canvas, x, y, self.w, self.col)
        elif self.typ == "truck":  draw_truck(canvas, x, y, self.w, self.col)
        elif self.typ == "log":    draw_log(canvas, x, y, self.w)
        elif self.typ == "turtle": draw_turtle(canvas, x, y, self.w)


class Frogger:
    def __init__(self, root):
        self.root = root
        self.root.title("Frogger")
        self.root.resizable(False, False)
        self.root.configure(bg="black")

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                                bg=C_BG, highlightthickness=0)
        self.canvas.pack()

        self.grass = {r: [(random.randint(0, WIDTH-2), random.randint(4, 11))
                          for _ in range(50)]
                      for r in range(ROWS)}

        self.best    = 0
        self.running = False

        self._init_state()
        self._title_screen()

        self.root.bind("<KeyPress>", self._on_key)
        self.root.focus_set()

    def _init_state(self):
        self.score     = 0
        self.lives     = 3
        self.homes     = [False] * len(HOME_COLS)
        self.dead      = False
        self.death_t   = 0.0
        self.time_left = TIME_LIMIT
        self.last_t    = None
        self._spawn_objects()
        self._reset_frog()

    def _spawn_objects(self):
        self.objects = []
        for (row, spd, direc, typ, col, wc, count) in LANES:
            gap = WIDTH // count
            for i in range(count):
                x = i * gap + random.randint(0, max(0, gap - wc * CELL))
                self.objects.append(LaneObj(row, x, spd, direc, typ, col, wc))

    def _reset_frog(self):
        self.frog_col  = COLS // 2
        self.frog_row  = 12
        self.frog_x    = float(self.frog_col * CELL + CELL // 2)
        self.frog_y    = float(row_y(12) + CELL // 2)
        self.frog_ride = None
        self.dead      = False
        self.death_t   = 0.0
        self.time_left = TIME_LIMIT
        self.last_t    = None

    def _title_screen(self):
        self.canvas.delete("all")
        self._draw_bg()
        cx, cy = WIDTH // 2, HEIGHT // 2 - 20
        self.canvas.create_rectangle(cx-200, cy-80, cx+200, cy+110,
                                     fill="#000020", outline="#00ff7f", width=2)
        self.canvas.create_text(cx, cy-40, text="FROGGER",
            font=("Courier", 42, "bold"), fill="#00ff7f")
        draw_frog(self.canvas, cx, cy+30)
        self.canvas.create_text(cx, cy+85,
            text="ENTER  para jogar", font=("Courier", 15), fill=C_TEXT)
        self.canvas.create_text(cx, HEIGHT-16,
            text="Setas  mover   |   R  reiniciar",
            font=("Courier", 11), fill="#777")

    def _start_game(self):
        self._init_state()
        self.running = True
        self.last_t  = time.time()
        self._loop()

    def _restart(self):
        self.running = False
        self.root.after(80, self._start_game)

    def _loop(self):
        if not self.running:
            return
        now = time.time()
        dt  = min(now - (self.last_t or now), 0.1)
        self.last_t = now
        self._update(dt)
        self._render()
        self.root.after(FRAME_MS, self._loop)

    def _update(self, dt):
        if self.dead:
            self.death_t -= dt
            if self.death_t <= 0:
                self.lives -= 1
                if self.lives <= 0:
                    self._game_over()
                    return
                self._reset_frog()
            return

        self.time_left -= dt
        if self.time_left <= 0:
            self._kill_frog(); return

        for obj in self.objects:
            obj.update(dt)

        if self.frog_row in RIVER_ROWS:
            ride = self.frog_ride
            if ride is None:
                self._kill_frog(); return
            if not (ride.left() - 8 < self.frog_x < ride.right() + 8):
                self._kill_frog(); return
            self.frog_x += ride.spd * ride.dir * dt
            if self.frog_x < 2 or self.frog_x > WIDTH - 2:
                self._kill_frog(); return

        if self.frog_row in ROAD_ROWS:
            fx1, fx2 = self.frog_x - 16, self.frog_x + 16
            fy1 = row_y(self.frog_row) + 5
            fy2 = fy1 + CELL - 8
            for obj in self.objects:
                if obj.row != self.frog_row: continue
                if obj.left()+6 < fx2 and obj.right()-6 > fx1:
                    if obj.top()+2 < fy2 and obj.bot()-2 > fy1:
                        self._kill_frog(); return

    def _on_key(self, event):
        k = event.keysym

        if not self.running:
            if k == "Return":
                self._start_game()
            return

        if k.lower() == "r":
            self._restart(); return

        if self.dead: return

        dirs = {
            "Up": (0,-1), "Down": (0,1), "Left": (-1,0), "Right": (1,0),
            "w":  (0,-1), "s":   (0, 1), "a":   (-1, 0), "d":    (1, 0),
        }
        if k not in dirs: return

        dc, dr = dirs[k]
        nc = self.frog_col + dc
        nr = self.frog_row + dr

        if not (0 <= nc < COLS) or not (0 <= nr < ROWS):
            return

        self.frog_col  = nc
        self.frog_row  = nr
        self.frog_x    = float(nc * CELL + CELL // 2)
        self.frog_y    = float(row_y(nr) + CELL // 2)
        self.frog_ride = None
        self.score    += 10

        if self.frog_row in RIVER_ROWS:
            self._find_ride()
        elif self.frog_row == HOME_ROW:
            self._check_home()

    def _find_ride(self):
        for obj in self.objects:
            if obj.row != self.frog_row: continue
            if obj.typ not in ("log", "turtle"): continue
            if obj.left() - 8 < self.frog_x < obj.right() + 8:
                self.frog_ride = obj
                return
        self._kill_frog()

    def _check_home(self):
        for i, hc in enumerate(HOME_COLS):
            hx = hc * CELL + CELL // 2
            if abs(self.frog_x - hx) <= CELL // 2 + 6:
                if self.homes[i]:
                    self._kill_frog(); return
                self.homes[i] = True
                self.score += 100 + int(self.time_left * 5)
                if all(self.homes):
                    self._win(); return
                self._reset_frog()
                return
        self._kill_frog()

    def _kill_frog(self):
        if self.dead: return
        self.dead    = True
        self.death_t = 1.5

    def _game_over(self):
        self.running = False
        if self.score > self.best: self.best = self.score
        self._render()
        cx, cy = WIDTH // 2, HEIGHT // 2
        self.canvas.create_rectangle(cx-170, cy-70, cx+170, cy+85,
                                     fill="#000020", outline="#eb4d4b", width=2)
        self.canvas.create_text(cx, cy-30, text="GAME OVER",
            font=("Courier", 30, "bold"), fill="#eb4d4b")
        self.canvas.create_text(cx, cy+15,
            text=f"Pontuacao: {self.score}", font=("Courier", 16), fill=C_TEXT)
        self.canvas.create_text(cx, cy+52,
            text="R  para reiniciar", font=("Courier", 13), fill=C_SCORE)

    def _win(self):
        self.running = False
        if self.score > self.best: self.best = self.score
        self._render()
        cx, cy = WIDTH // 2, HEIGHT // 2
        self.canvas.create_rectangle(cx-190, cy-70, cx+190, cy+85,
                                     fill="#000020", outline="#00ff7f", width=2)
        self.canvas.create_text(cx, cy-30, text="VOCE VENCEU!",
            font=("Courier", 26, "bold"), fill="#00ff7f")
        self.canvas.create_text(cx, cy+15,
            text=f"Pontuacao: {self.score}", font=("Courier", 16), fill=C_TEXT)
        self.canvas.create_text(cx, cy+52,
            text="R  para jogar novamente", font=("Courier", 13), fill=C_SCORE)

    def _draw_bg(self):
        for r in range(ROWS):
            y1, y2 = row_y(r), row_y(r) + CELL
            if r == HOME_ROW:
                self.canvas.create_rectangle(0, y1, WIDTH, y2, fill=C_WATER, outline="")
                for i, hc in enumerate(HOME_COLS):
                    hx = hc * CELL
                    fill    = C_HOME_FILL if self.homes[i] else C_HOME_OPEN
                    outline = "#00ff7f"   if self.homes[i] else "#1a5276"
                    self.canvas.create_rectangle(hx+3, y1+3, hx+CELL-3, y2-3,
                                                 fill=fill, outline=outline, width=2)
            elif r in RIVER_ROWS:
                col = C_WATER if r % 2 == 0 else C_WATER2
                self.canvas.create_rectangle(0, y1, WIDTH, y2, fill=col, outline="")
            elif r in ROAD_ROWS:
                col = C_ROAD if r % 2 == 0 else "#242424"
                self.canvas.create_rectangle(0, y1, WIDTH, y2, fill=col, outline="")
                for lx in range(0, WIDTH, 40):
                    self.canvas.create_rectangle(lx, y1+CELL//2-2, lx+22,
                                                 y1+CELL//2+2, fill="#555533", outline="")
            else:
                self.canvas.create_rectangle(0, y1, WIDTH, y2, fill=C_GRASS, outline="")
                for gx, gh in self.grass[r]:
                    self.canvas.create_line(gx, y2, gx, y2-gh, fill="#2a8a2a", width=2)

    def _draw_hud(self):
        self.canvas.create_rectangle(0, 0, WIDTH, 60, fill="#0a0a18", outline="")
        self.canvas.create_line(0, 59, WIDTH, 59, fill="#2a2a3a")

        self.canvas.create_text(12, 10, anchor="nw",
            text=f"PONTOS: {self.score:05d}", font=("Courier", 14, "bold"), fill=C_SCORE)
        self.canvas.create_text(12, 35, anchor="nw",
            text=f"RECORDE: {self.best:05d}", font=("Courier", 11), fill="#aaaaaa")

        for i in range(self.lives):
            draw_frog(self.canvas, WIDTH - 26 - i * 38, 30)

        bar_x, bar_y = WIDTH // 2 - 80, 10
        bar_w, bar_h = 160, 16
        ratio = max(0.0, self.time_left / TIME_LIMIT)
        tc = C_TIME_OK if ratio > 0.5 else (C_TIME_WARN if ratio > 0.25 else C_TIME_BAD)
        self.canvas.create_rectangle(bar_x, bar_y, bar_x+bar_w, bar_y+bar_h,
                                     fill="#111", outline="#333")
        if ratio > 0:
            self.canvas.create_rectangle(bar_x, bar_y,
                                         bar_x+int(bar_w*ratio), bar_y+bar_h,
                                         fill=tc, outline="")
        self.canvas.create_text(WIDTH // 2, 38,
            text=f"{self.time_left:.1f}s", font=("Courier", 11), fill=tc)

        homes_txt = "  ".join(("X" if h else "o") for h in self.homes)
        self.canvas.create_text(WIDTH // 2, 9, anchor="n",
            text=homes_txt, font=("Courier", 9), fill=C_SCORE)

    def _render(self):
        self.canvas.delete("all")
        self._draw_bg()
        for obj in self.objects:
            obj.draw(self.canvas)
        if self.dead:
            if int(self.death_t * 8) % 2 == 0:
                draw_frog(self.canvas, int(self.frog_x), int(self.frog_y), dead=True)
        else:
            draw_frog(self.canvas, int(self.frog_x), int(self.frog_y))
        self._draw_hud()


if __name__ == "__main__":
    root = tk.Tk()
    game = Frogger(root)
    root.mainloop()