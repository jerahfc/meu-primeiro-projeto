import tkinter as tk
import random
import time

# ── Configurações ──────────────────────────────────────────────
WIDTH, HEIGHT  = 700, 750
FPS            = 60
FRAME_MS       = 1000 // FPS

# Cores
BG             = "#000008"
STAR_COLORS    = ["#ffffff", "#aaaaff", "#ffaaaa", "#aaffaa"]
PLAYER_COLOR   = "#00ff88"
BULLET_COLOR   = "#ffff00"
ALIEN_BULLET   = "#ff4444"
SHIELD_COLOR   = "#00cc66"
TEXT_COLOR     = "#ffffff"
SCORE_COLOR    = "#00ff88"
LIFE_COLOR     = "#ff4444"

# Nave do jogador
PLAYER_W, PLAYER_H = 50, 30
PLAYER_SPEED       = 5
PLAYER_Y           = HEIGHT - 80
BULLET_SPEED       = 10
MAX_PLAYER_BULLETS = 2

# Aliens
ALIEN_COLS   = 11
ALIEN_ROWS   = 5
ALIEN_W, ALIEN_H = 36, 28
ALIEN_PAD_X  = 16
ALIEN_PAD_Y  = 20
ALIEN_START_X = 60
ALIEN_START_Y = 80
ALIEN_DROP    = 18
ALIEN_SHOOT_CHANCE = 0.0015  # por alien por frame

# Escudos
SHIELD_COUNT  = 4
SHIELD_W, SHIELD_H = 64, 44
SHIELD_Y      = HEIGHT - 150
BLOCK_SIZE    = 8


# ── Sprites ASCII (desenhados no canvas) ──────────────────────
def draw_player(canvas, x, y, color=PLAYER_COLOR):
    """Nave do jogador em forma de foguete."""
    # corpo
    canvas.create_polygon(
        x, y - PLAYER_H // 2,
        x + PLAYER_W // 2, y + PLAYER_H // 2,
        x - PLAYER_W // 2, y + PLAYER_H // 2,
        fill=color, outline="")
    # canhão
    canvas.create_rectangle(x - 3, y - PLAYER_H // 2 - 10,
                             x + 3, y - PLAYER_H // 2 + 2,
                             fill=color, outline="")
    # asas
    canvas.create_polygon(
        x - PLAYER_W // 2, y + PLAYER_H // 2,
        x - PLAYER_W // 2 - 10, y + PLAYER_H // 2 + 8,
        x - PLAYER_W // 4, y + PLAYER_H // 2,
        fill=color, outline="")
    canvas.create_polygon(
        x + PLAYER_W // 2, y + PLAYER_H // 2,
        x + PLAYER_W // 2 + 10, y + PLAYER_H // 2 + 8,
        x + PLAYER_W // 4, y + PLAYER_H // 2,
        fill=color, outline="")


def draw_alien(canvas, x, y, atype, frame, color):
    """Alien com 2 frames de animação."""
    cx, cy = x + ALIEN_W // 2, y + ALIEN_H // 2
    f = frame % 2  # 0 ou 1

    if atype == 0:  # Tipo A – polvo (linha 0)
        # corpo
        canvas.create_oval(cx - 14, cy - 10, cx + 14, cy + 8, fill=color, outline="")
        # olhos
        canvas.create_oval(cx - 8, cy - 6, cx - 3, cy - 1, fill="black", outline="")
        canvas.create_oval(cx + 3, cy - 6, cx + 8, cy - 1, fill="black", outline="")
        # tentáculos (alternados)
        offsets = [-12, -4, 4, 12] if f == 0 else [-14, -5, 5, 14]
        for ox in offsets:
            canvas.create_line(cx + ox, cy + 8, cx + ox, cy + 16,
                                fill=color, width=2)

    elif atype == 1:  # Tipo B – caranguejo (linhas 1-2)
        canvas.create_rectangle(cx - 14, cy - 8, cx + 14, cy + 8, fill=color, outline="")
        canvas.create_oval(cx - 10, cy - 5, cx - 4, cy + 2, fill="black", outline="")
        canvas.create_oval(cx + 4, cy - 5, cx + 10, cy + 2, fill="black", outline="")
        # antenas
        if f == 0:
            canvas.create_line(cx - 10, cy - 8, cx - 16, cy - 16, fill=color, width=2)
            canvas.create_line(cx + 10, cy - 8, cx + 16, cy - 16, fill=color, width=2)
            canvas.create_line(cx - 14, cy + 2,  cx - 20, cy + 10, fill=color, width=2)
            canvas.create_line(cx + 14, cy + 2,  cx + 20, cy + 10, fill=color, width=2)
        else:
            canvas.create_line(cx - 10, cy - 8, cx - 14, cy - 17, fill=color, width=2)
            canvas.create_line(cx + 10, cy - 8, cx + 14, cy - 17, fill=color, width=2)
            canvas.create_line(cx - 14, cy + 4,  cx - 18, cy + 12, fill=color, width=2)
            canvas.create_line(cx + 14, cy + 4,  cx + 18, cy + 12, fill=color, width=2)

    else:  # Tipo C – disco voador (linhas 3-4)
        canvas.create_oval(cx - 16, cy - 6, cx + 16, cy + 8, fill=color, outline="")
        canvas.create_oval(cx - 8,  cy - 12, cx + 8,  cy - 4, fill=color, outline="")
        canvas.create_oval(cx - 5, cy - 3, cx - 1, cy + 1, fill="black", outline="")
        canvas.create_oval(cx + 1, cy - 3, cx + 5,  cy + 1, fill="black", outline="")
        lights = [-10, -4, 4, 10] if f == 0 else [-8, -2, 2, 8]
        light_color = "#ffff00" if f == 0 else "#ff8800"
        for lx in lights:
            canvas.create_oval(cx + lx - 2, cy + 4, cx + lx + 2, cy + 8,
                                fill=light_color, outline="")


def alien_color(row):
    return ["#ff6688", "#ff9944", "#ffcc00", "#44ddff", "#aa66ff"][row]


def alien_score(row):
    return [30, 20, 20, 10, 10][row]


def alien_type(row):
    return [0, 1, 1, 2, 2][row]


# ── Jogo ───────────────────────────────────────────────────────
class SpaceInvaders:
    def __init__(self, root):
        self.root = root
        self.root.title("👾 Space Invaders")
        self.root.resizable(False, False)
        self.root.configure(bg="black")

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                                bg=BG, highlightthickness=0)
        self.canvas.pack()

        self.keys = set()
        self.root.bind("<KeyPress>",   lambda e: self.keys.add(e.keysym))
        self.root.bind("<KeyRelease>", lambda e: self.keys.discard(e.keysym))
        self.root.bind("<KeyPress-r>", lambda e: self._restart())
        self.root.bind("<KeyPress-R>", lambda e: self._restart())
        self.root.bind("<space>",      lambda e: self._fire())

        # estrelas estáticas
        self.stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT),
                       random.choice(STAR_COLORS), random.randint(1, 2))
                      for _ in range(120)]

        self._init_state()
        self._title_screen()

    # ── Estado ─────────────────────────────────────────────────
    def _init_state(self):
        self.score     = 0
        self.lives     = 3
        self.level     = 1
        self.running   = False
        self.game_over = False
        self.won       = False
        self.frame     = 0
        self.anim_tick = 0

        # Jogador
        self.px      = WIDTH // 2
        self.py      = PLAYER_Y
        self.p_bullets = []   # [(x, y)]
        self.last_fire = 0

        # Aliens: {(row, col): alive}
        self.aliens   = {}
        self.alien_frame = 0
        speed = max(0.4, 1.2 - (self.level - 1) * 0.1)
        self.alien_dx = speed
        self.alien_dy = 0
        self.a_bullets = []   # [(x, y)]

        for r in range(ALIEN_ROWS):
            for c in range(ALIEN_COLS):
                self.aliens[(r, c)] = True

        self.alien_x_off = 0
        self.alien_y_off = 0
        self.alien_dir   = 1   # 1=direita, -1=esquerda
        self.alien_move_timer = 0
        self.alien_move_interval = max(4, 20 - (self.level - 1) * 2)

        # Explosões: [(x, y, timer)]
        self.explosions = []

        # Escudos: grid de blocos {(si, bx, by): True}
        self.shields = {}
        for si in range(SHIELD_COUNT):
            sx = int(WIDTH * (si + 1) / (SHIELD_COUNT + 1)) - SHIELD_W // 2
            sy = SHIELD_Y
            for bx in range(0, SHIELD_W, BLOCK_SIZE):
                for by in range(0, SHIELD_H, BLOCK_SIZE):
                    # forma arredondada
                    nx = bx // BLOCK_SIZE
                    ny = by // BLOCK_SIZE
                    cols_n = SHIELD_W // BLOCK_SIZE
                    rows_n = SHIELD_H // BLOCK_SIZE
                    if (nx == 0 or nx == cols_n - 1) and ny == 0:
                        continue
                    if ny == rows_n - 1 and (cols_n // 3 <= nx <= 2 * cols_n // 3):
                        continue
                    self.shields[(si, bx, by)] = {
                        'x': sx + bx, 'y': sy + by
                    }

    def _shield_origin(self, si):
        return int(WIDTH * (si + 1) / (SHIELD_COUNT + 1)) - SHIELD_W // 2, SHIELD_Y

    # ── Telas ──────────────────────────────────────────────────
    def _title_screen(self):
        self.canvas.delete("all")
        self._draw_stars()
        y = HEIGHT // 2 - 80
        self.canvas.create_text(WIDTH // 2, y,
            text="SPACE INVADERS", font=("Courier", 40, "bold"),
            fill=SCORE_COLOR)
        self.canvas.create_text(WIDTH // 2, y + 70,
            text="👾  👾  👾  👾  👾  👾", font=("Courier", 22), fill="#ff6688")
        self.canvas.create_text(WIDTH // 2, y + 130,
            text="ENTER  para iniciar", font=("Courier", 16), fill=TEXT_COLOR)
        self.canvas.create_text(WIDTH // 2, y + 165,
            text="← →  mover   |   ESPAÇO  atirar   |   R  reiniciar",
            font=("Courier", 11), fill="#888888")
        self.root.bind("<Return>", lambda _: self._start_game())

    def _start_game(self):
        self.root.unbind("<Return>")
        self._init_state()
        self.running = True
        self._loop()

    def _restart(self):
        self.running = False
        self.level   = 1
        self.score   = 0
        self.root.after(50, self._start_game)

    def _next_level(self):
        self.running = False
        self.level  += 1
        old_score    = self.score
        self._init_state()
        self.score   = old_score
        self.running = True
        self._loop()

    # ── Loop ───────────────────────────────────────────────────
    def _loop(self):
        if not self.running:
            return
        t0 = time.time()
        self._update()
        self._render()
        elapsed = int((time.time() - t0) * 1000)
        delay   = max(1, FRAME_MS - elapsed)
        if self.running:
            self.root.after(delay, self._loop)

    def _update(self):
        self.frame += 1

        # ── Movimento do jogador ──
        if "Left" in self.keys or "a" in self.keys:
            self.px = max(PLAYER_W // 2 + 5, self.px - PLAYER_SPEED)
        if "Right" in self.keys or "d" in self.keys:
            self.px = min(WIDTH - PLAYER_W // 2 - 5, self.px + PLAYER_SPEED)

        # ── Balas do jogador ──
        self.p_bullets = [(bx, by - BULLET_SPEED)
                          for bx, by in self.p_bullets if by > 0]

        # ── Movimento dos aliens ──
        self.alien_move_timer += 1
        if self.alien_move_timer >= self.alien_move_interval:
            self.alien_move_timer = 0
            self.alien_frame ^= 1

            alive = [k for k, v in self.aliens.items() if v]
            if not alive:
                self._win(); return

            max_x = max(ALIEN_START_X + c * (ALIEN_W + ALIEN_PAD_X) + self.alien_x_off
                        for (r, c) in alive)
            min_x = min(ALIEN_START_X + c * (ALIEN_W + ALIEN_PAD_X) + self.alien_x_off
                        for (r, c) in alive)

            step = (ALIEN_W + ALIEN_PAD_X) * 0.4 * self.alien_dir
            if self.alien_dir == 1 and max_x + ALIEN_W + step > WIDTH - 10:
                self.alien_y_off += ALIEN_DROP
                self.alien_dir    = -1
            elif self.alien_dir == -1 and min_x + step < 10:
                self.alien_y_off += ALIEN_DROP
                self.alien_dir    = 1
            else:
                self.alien_x_off += step

        # ── Tiro dos aliens ──
        alive = [(r, c) for (r, c), v in self.aliens.items() if v]
        for (r, c) in alive:
            # só a linha mais baixa de cada coluna atira
            col_aliens = [(rr, cc) for rr, cc in alive if cc == c]
            max_row    = max(rr for rr, _ in col_aliens)
            if r == max_row and random.random() < ALIEN_SHOOT_CHANCE * (1 + self.level * 0.2):
                ax = ALIEN_START_X + c * (ALIEN_W + ALIEN_PAD_X) + self.alien_x_off + ALIEN_W // 2
                ay = ALIEN_START_Y + r * (ALIEN_H + ALIEN_PAD_Y) + self.alien_y_off + ALIEN_H
                self.a_bullets.append([ax, ay])

        self.a_bullets = [[bx, by + 5] for bx, by in self.a_bullets if by < HEIGHT]

        # ── Colisões: bala jogador × aliens ──
        for bx, by in list(self.p_bullets):
            for (r, c), alive_f in list(self.aliens.items()):
                if not alive_f: continue
                ax = ALIEN_START_X + c * (ALIEN_W + ALIEN_PAD_X) + self.alien_x_off
                ay = ALIEN_START_Y + r * (ALIEN_H + ALIEN_PAD_Y) + self.alien_y_off
                if ax <= bx <= ax + ALIEN_W and ay <= by <= ay + ALIEN_H:
                    self.aliens[(r, c)] = False
                    self.score         += alien_score(r)
                    self.explosions.append([bx, by, 15])
                    if (bx, by) in self.p_bullets:
                        self.p_bullets.remove((bx, by))
                    # acelera quando poucas naves restam
                    remaining = sum(v for v in self.aliens.values())
                    if remaining > 0:
                        self.alien_move_interval = max(2, int(20 - (55 - remaining) * 0.3
                                                                - (self.level - 1) * 2))
                    break

        # ── Colisões: bala jogador × escudos ──
        for bx, by in list(self.p_bullets):
            for key in list(self.shields):
                b = self.shields[key]
                if b['x'] <= bx <= b['x'] + BLOCK_SIZE and b['y'] <= by <= b['y'] + BLOCK_SIZE:
                    del self.shields[key]
                    if (bx, by) in self.p_bullets:
                        self.p_bullets.remove((bx, by))
                    break

        # ── Colisões: bala alien × escudos ──
        for bullet in list(self.a_bullets):
            bx, by = bullet
            for key in list(self.shields):
                b = self.shields[key]
                if b['x'] <= bx <= b['x'] + BLOCK_SIZE and b['y'] <= by <= b['y'] + BLOCK_SIZE:
                    del self.shields[key]
                    self.a_bullets.remove(bullet)
                    break

        # ── Colisões: bala alien × jogador ──
        for bullet in list(self.a_bullets):
            bx, by = bullet
            if (self.px - PLAYER_W // 2 <= bx <= self.px + PLAYER_W // 2 and
                    self.py - PLAYER_H // 2 <= by <= self.py + PLAYER_H // 2):
                self.lives -= 1
                self.explosions.append([self.px, self.py, 30])
                self.a_bullets.remove(bullet)
                if self.lives <= 0:
                    self._end_game(); return
                break

        # ── Aliens chegaram embaixo ──
        for (r, c), alive_f in self.aliens.items():
            if not alive_f: continue
            ay = ALIEN_START_Y + r * (ALIEN_H + ALIEN_PAD_Y) + self.alien_y_off
            if ay + ALIEN_H >= PLAYER_Y - PLAYER_H // 2:
                self._end_game(); return

        # ── Explosões ──
        self.explosions = [[x, y, t - 1] for x, y, t in self.explosions if t > 1]

        # ── Todos os aliens destruídos ──
        if not any(self.aliens.values()):
            self._win()

    def _fire(self):
        if not self.running or self.game_over: return
        if len(self.p_bullets) < MAX_PLAYER_BULLETS:
            now = time.time()
            if now - self.last_fire > 0.25:
                self.p_bullets.append((self.px, self.py - PLAYER_H // 2 - 12))
                self.last_fire = now

    def _end_game(self):
        self.running   = False
        self.game_over = True
        self._render()
        self.canvas.create_rectangle(WIDTH // 4 - 10, HEIGHT // 2 - 80,
                                     WIDTH * 3 // 4 + 10, HEIGHT // 2 + 90,
                                     fill="#000020", outline=LIFE_COLOR, width=2)
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 - 45,
            text="GAME OVER", font=("Courier", 32, "bold"), fill=LIFE_COLOR)
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 5,
            text=f"Pontuação: {self.score}", font=("Courier", 16), fill=TEXT_COLOR)
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 45,
            text="R  para reiniciar", font=("Courier", 13), fill=SCORE_COLOR)

    def _win(self):
        self.running = False
        self._render()
        self.canvas.create_rectangle(WIDTH // 4 - 10, HEIGHT // 2 - 80,
                                     WIDTH * 3 // 4 + 10, HEIGHT // 2 + 90,
                                     fill="#000020", outline=SCORE_COLOR, width=2)
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 - 45,
            text="FASE CONCLUÍDA!", font=("Courier", 28, "bold"), fill=SCORE_COLOR)
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 5,
            text=f"Pontuação: {self.score}  |  Nível {self.level}",
            font=("Courier", 15), fill=TEXT_COLOR)
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 45,
            text="ENTER  para próximo nível",
            font=("Courier", 13), fill=SCORE_COLOR)
        self.root.bind("<Return>", lambda _: self._advance())

    def _advance(self):
        self.root.unbind("<Return>")
        self._next_level()

    # ── Renderização ───────────────────────────────────────────
    def _draw_stars(self):
        for sx, sy, sc, sr in self.stars:
            # leve cintilação
            if random.random() < 0.01:
                sc = random.choice(STAR_COLORS)
            self.canvas.create_oval(sx - sr, sy - sr, sx + sr, sy + sr,
                                    fill=sc, outline="")

    def _render(self):
        self.canvas.delete("all")
        self._draw_stars()

        # HUD
        self.canvas.create_text(12, 12, anchor="nw",
            text=f"PONTOS: {self.score:05d}", font=("Courier", 14, "bold"),
            fill=SCORE_COLOR)
        self.canvas.create_text(WIDTH // 2, 12, anchor="n",
            text=f"NÍVEL  {self.level}", font=("Courier", 14, "bold"),
            fill=TEXT_COLOR)
        for i in range(self.lives):
            lx = WIDTH - 30 - i * 28
            self.canvas.create_polygon(
                lx, 8, lx + 10, 24, lx - 10, 24,
                fill=LIFE_COLOR, outline="")

        # Linha separadora
        self.canvas.create_line(0, 36, WIDTH, 36, fill="#333333")

        # Escudos
        for key, b in self.shields.items():
            self.canvas.create_rectangle(
                b['x'], b['y'], b['x'] + BLOCK_SIZE, b['y'] + BLOCK_SIZE,
                fill=SHIELD_COLOR, outline="")

        # Aliens
        for (r, c), alive_f in self.aliens.items():
            if not alive_f: continue
            ax = int(ALIEN_START_X + c * (ALIEN_W + ALIEN_PAD_X) + self.alien_x_off)
            ay = int(ALIEN_START_Y + r * (ALIEN_H + ALIEN_PAD_Y) + self.alien_y_off)
            draw_alien(self.canvas, ax, ay, alien_type(r),
                       self.alien_frame, alien_color(r))

        # Jogador
        if not self.game_over:
            draw_player(self.canvas, self.px, self.py)

        # Linha do chão
        self.canvas.create_line(0, PLAYER_Y + PLAYER_H // 2 + 15,
                                  WIDTH, PLAYER_Y + PLAYER_H // 2 + 15,
                                  fill=SCORE_COLOR, width=2)

        # Balas do jogador
        for bx, by in self.p_bullets:
            self.canvas.create_rectangle(bx - 2, by - 8, bx + 2, by + 2,
                                          fill=BULLET_COLOR, outline="")

        # Balas dos aliens
        for bx, by in self.a_bullets:
            self.canvas.create_polygon(
                bx, by - 8, bx + 4, by, bx, by + 4, bx - 4, by,
                fill=ALIEN_BULLET, outline="")

        # Explosões
        for ex, ey, t in self.explosions:
            r_val = int(t * 2.5)
            alpha = t / 30
            colors = ["#ff8800", "#ffff00", "#ff4400"]
            for i, ec in enumerate(colors):
                rr = r_val - i * 3
                if rr > 0:
                    self.canvas.create_oval(ex - rr, ey - rr,
                                             ex + rr, ey + rr,
                                             fill=ec, outline="")


# ── Main ───────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    game = SpaceInvaders(root)
    root.mainloop()