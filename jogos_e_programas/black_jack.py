import tkinter as tk
import random

# ═══════════════════════════════════════════════════════════════
#  CONFIGURAÇÕES
# ═══════════════════════════════════════════════════════════════
WIDTH, HEIGHT = 860, 600

BG_TABLE  = "#0a5c2a"
BG_DARK   = "#063d1c"
C_TEXT    = "#ffffff"
C_GOLD    = "#f9ca24"
C_CARD_BG = "#fdf6e3"
C_RED     = "#cc2200"
C_BLACK   = "#111111"
C_BLUE    = "#1a3a6a"

CARD_W, CARD_H = 70, 100
SUITS  = ["♠", "♥", "♦", "♣"]
RANKS  = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]

CHIPS = [
    (1,   "#ecf0f1"),
    (5,   "#e74c3c"),
    (10,  "#3498db"),
    (25,  "#2ecc71"),
    (100, "#9b59b6"),
]

# ═══════════════════════════════════════════════════════════════
#  LÓGICA DAS CARTAS
# ═══════════════════════════════════════════════════════════════
def make_deck(num=6):
    deck = [(r, s) for _ in range(num) for s in SUITS for r in RANKS]
    random.shuffle(deck)
    return deck

def card_val(rank):
    if rank in ("J","Q","K"): return 10
    if rank == "A":           return 11
    return int(rank)

def total(hand):
    t    = sum(card_val(r) for r,s in hand)
    aces = sum(1 for r,s in hand if r == "A")
    while t > 21 and aces:
        t -= 10; aces -= 1
    return t

def label(hand):
    t    = total(hand)
    raw  = sum(card_val(r) for r,s in hand)
    soft = (raw != t) and any(r=="A" for r,s in hand)
    return ("Soft " if soft and t<=21 else "") + str(t)

# ═══════════════════════════════════════════════════════════════
#  JOGO
# ═══════════════════════════════════════════════════════════════
class Game:
    def __init__(self, root):
        self.root    = root
        self.root.title("Jogo 21 — Blackjack")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_DARK)

        self.cv = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                            bg=BG_TABLE, highlightthickness=0)
        self.cv.pack()

        self.deck    = make_deck()
        self.balance = 1000
        self.bet     = 0
        self.phase   = "bet"   # bet | play | over

        self.player  = []
        self.dealer  = []
        self.msg     = ""
        self.msg_col = C_GOLD

        self.root.bind("<KeyPress>", self._key)
        self.draw()

    # ── baralho ───────────────────────────────────────────────
    def deal(self):
        if len(self.deck) < 15:
            self.deck = make_deck()
        return self.deck.pop()

    # ── teclas de atalho ──────────────────────────────────────
    def _key(self, e):
        k = e.keysym.lower()
        if self.phase == "bet":
            if k in ("1","2","3","4","5"):
                self.add_chip({"1":1,"2":5,"3":10,"4":25,"5":100}[k])
            elif k == "c":
                self.clear_bet()
            elif k == "return" and self.bet > 0:
                self.start_round()
        elif self.phase == "play":
            if k == "h":   self.hit()
            elif k == "s": self.stand()
            elif k == "d": self.double()
        elif self.phase == "over":
            if k == "return" or k == "n":
                self.new_round()

    # ── apostas ───────────────────────────────────────────────
    def add_chip(self, v):
        if self.phase != "bet": return
        if v > self.balance:    return
        self.bet     += v
        self.balance -= v
        self.draw()

    def clear_bet(self):
        if self.phase != "bet": return
        self.balance += self.bet
        self.bet      = 0
        self.draw()

    # ── rodada ────────────────────────────────────────────────
    def start_round(self):
        if self.phase != "bet" or self.bet == 0: return
        self.player = [self.deal(), self.deal()]
        self.dealer = [self.deal(), self.deal()]
        self.phase  = "play"
        self.msg    = ""
        if total(self.player) == 21:
            self.finish()
        else:
            self.draw()

    def hit(self):
        if self.phase != "play": return
        self.player.append(self.deal())
        if total(self.player) >= 21:
            self.finish()
        else:
            self.draw()

    def stand(self):
        if self.phase != "play": return
        while total(self.dealer) < 17:
            self.dealer.append(self.deal())
        self.finish()

    def double(self):
        if self.phase != "play":          return
        if len(self.player) != 2:         return
        if self.balance < self.bet:       return
        self.balance -= self.bet
        self.bet     *= 2
        self.player.append(self.deal())
        while total(self.dealer) < 17:
            self.dealer.append(self.deal())
        self.finish()

    def finish(self):
        self.phase = "over"
        pt = total(self.player)
        dt = total(self.dealer)
        bj_p = pt == 21 and len(self.player) == 2
        bj_d = dt == 21 and len(self.dealer) == 2

        if pt > 21:
            self.msg     = "💥  Você estourou!  Perdeu."
            self.msg_col = "#eb4d4b"
        elif bj_p and not bj_d:
            win = int(self.bet * 1.5)
            self.balance += self.bet + win
            self.msg     = f"🃏  BLACKJACK!  +${win}"
            self.msg_col = C_GOLD
        elif bj_d and not bj_p:
            self.msg     = "🃏  Blackjack do dealer.  Perdeu."
            self.msg_col = "#eb4d4b"
        elif dt > 21:
            self.balance += self.bet * 2
            self.msg     = f"🎉  Dealer estourou!  +${self.bet}"
            self.msg_col = "#2ecc71"
        elif pt > dt:
            self.balance += self.bet * 2
            self.msg     = f"✅  Você venceu!  +${self.bet}"
            self.msg_col = "#2ecc71"
        elif pt == dt:
            self.balance += self.bet
            self.msg     = "🤝  Empate.  Aposta devolvida."
            self.msg_col = "#95a5a6"
        else:
            self.msg     = f"❌  Dealer venceu.  -{self.bet}"
            self.msg_col = "#eb4d4b"

        self.bet = 0
        self.draw()

    def new_round(self):
        if self.balance <= 0:
            self.balance = 1000
        self.phase  = "bet"
        self.bet    = 0
        self.player = []
        self.dealer = []
        self.msg    = ""
        self.draw()

    # ═══════════════════════════════════════════════════════════
    #  RENDERIZAÇÃO
    # ═══════════════════════════════════════════════════════════
    def draw(self):
        self.cv.delete("all")
        self._bg()
        self._hud()

        if self.phase == "bet":
            self._chips()
            self._prompt("Escolha sua aposta e clique em  Distribuir")
            self._btn(WIDTH//2-65, HEIGHT-58, 130, 40, "Distribuir",
                      "#8e44ad", self.start_round, enabled=(self.bet>0))
            self._btn(WIDTH//2-215, HEIGHT-58, 130, 40, "Limpar",
                      "#7f8c8d", self.clear_bet, enabled=(self.bet>0))

        elif self.phase == "play":
            self._hand(self.dealer, WIDTH//2, 60,  hide_hole=True,  label_txt="Dealer")
            self._hand(self.player, WIDTH//2, 310, hide_hole=False, label_txt="Você")
            can_dbl = len(self.player)==2 and self.balance>=self.bet
            self._btn(WIDTH//2-210, HEIGHT-58, 120, 40, "Pedir (H)",  "#27ae60", self.hit)
            self._btn(WIDTH//2- 60, HEIGHT-58, 120, 40, "Parar (S)",  "#c0392b", self.stand)
            self._btn(WIDTH//2+ 90, HEIGHT-58, 130, 40, "Dobrar (D)", "#2980b9", self.double, enabled=can_dbl)

        elif self.phase == "over":
            self._hand(self.dealer, WIDTH//2, 60,  hide_hole=False, label_txt="Dealer")
            self._hand(self.player, WIDTH//2, 310, hide_hole=False, label_txt="Você")
            self._result_banner()
            self._btn(WIDTH//2-75, HEIGHT-58, 150, 40, "Nova Rodada (N)",
                      "#8e44ad", self.new_round)

    def _bg(self):
        self.cv.create_oval(-150,-150, WIDTH+150, HEIGHT+100,
                            fill=BG_TABLE, outline="")
        self.cv.create_oval(40, 30, WIDTH-40, HEIGHT-30,
                            fill="", outline="#1a7a3a", width=2)
        self.cv.create_rectangle(0, 0, WIDTH, 28, fill=BG_DARK, outline="")
        self.cv.create_text(WIDTH//2, 14, text="B L A C K J A C K  —  J O G O  2 1",
                            font=("Courier", 11, "bold"), fill="#2ecc71")
        self.cv.create_text(WIDTH//2, HEIGHT//2-10, text="21",
                            font=("Georgia", 64, "bold"), fill="#0d7a38")

    def _hud(self):
        self.cv.create_text(70, HEIGHT-38,
                            text=f"💰  Saldo: ${self.balance}",
                            font=("Courier", 13, "bold"), fill=C_GOLD, anchor="w")
        if self.bet > 0:
            self.cv.create_text(WIDTH-70, HEIGHT-38,
                                text=f"Aposta: ${self.bet}",
                                font=("Courier", 13, "bold"), fill=C_TEXT, anchor="e")

    def _hand(self, hand, cx, y, hide_hole, label_txt):
        if not hand: return
        n   = len(hand)
        gap = min(CARD_W+10, (WIDTH-140) // max(n,1))
        sx  = cx - (n*gap)//2

        for i,(rank,suit) in enumerate(hand):
            face = not (hide_hole and i==1)
            self._card(sx + i*gap, y, rank, suit, face)

        if hide_hole:
            vis = [(r,s) for j,(r,s) in enumerate(hand) if j!=1]
            txt = f"{label_txt}: {label(vis)} + ?"
        else:
            t   = total(hand)
            txt = f"{label_txt}: {label(hand)}"
            if t > 21: txt += "  💥"
            if t == 21 and len(hand)==2: txt += "  🃏"

        col = "#eb4d4b" if (not hide_hole and total(hand)>21) else C_TEXT
        self.cv.create_text(cx, y+CARD_H+20, text=txt,
                            font=("Courier",13,"bold"), fill=col)

    def _card(self, x, y, rank, suit, face_up):
        sh = 4
        self.cv.create_rectangle(x+sh, y+sh, x+CARD_W+sh, y+CARD_H+sh,
                                 fill="#1a1a1a", outline="")
        if face_up:
            self.cv.create_rectangle(x, y, x+CARD_W, y+CARD_H,
                                     fill=C_CARD_BG, outline="#aaaaaa", width=1)
            red = suit in ("♥","♦")
            col = C_RED if red else C_BLACK
            self.cv.create_text(x+8,  y+13, text=rank, font=("Georgia",11,"bold"), fill=col)
            self.cv.create_text(x+8,  y+26, text=suit, font=("Georgia", 9),        fill=col)
            self.cv.create_text(x+CARD_W-8, y+CARD_H-13, text=rank,
                                font=("Georgia",11,"bold"), fill=col)
            self.cv.create_text(x+CARD_W-8, y+CARD_H-26, text=suit,
                                font=("Georgia", 9), fill=col)
            fs = 26 if rank=="10" else 30
            self.cv.create_text(x+CARD_W//2, y+CARD_H//2,
                                text=suit, font=("Arial",fs), fill=col)
        else:
            self.cv.create_rectangle(x, y, x+CARD_W, y+CARD_H,
                                     fill="#1a3a6a", outline="#2a4a8a", width=1)
            for dx in range(8, CARD_W-4, 10):
                for dy in range(8, CARD_H-4, 14):
                    self.cv.create_rectangle(x+dx, y+dy, x+dx+6, y+dy+8,
                                             fill="#2a5a9a", outline="#3a6aaa")

    def _chips(self):
        n  = len(CHIPS)
        sx = WIDTH//2 - (n*72)//2 + 36
        cy = HEIGHT//2 + 60
        self.cv.create_text(WIDTH//2, cy-42,
                            text="Clique nas fichas para apostar",
                            font=("Courier",11), fill="#aaaaaa")
        for i,(val,col) in enumerate(CHIPS):
            x = sx + i*72
            ok = val <= self.balance
            self._chip(x, cy, val, col, ok)

    def _chip(self, x, y, value, color, enabled):
        r   = 28
        col = color if enabled else "#555"
        txt = "#ffffff" if enabled else "#888"
        self.cv.create_oval(x-r+3, y-r+3, x+r+3, y+r+3,
                            fill="#111111", outline="")
        c = self.cv.create_oval(x-r, y-r, x+r, y+r,
                                fill=col, outline="white", width=2)
        self.cv.create_oval(x-r+6, y-r+6, x+r-6, y+r-6,
                            fill="", outline="white", width=1, dash=(3,3))
        t = self.cv.create_text(x, y, text=f"${value}",
                                font=("Courier",10,"bold"), fill=txt)
        if enabled:
            for item in (c, t):
                self.cv.tag_bind(item, "<Button-1>",
                                 lambda e, v=value: self.add_chip(v))

    def _btn(self, x, y, w, h, text, color, cmd, enabled=True):
        col = color if enabled else "#444"
        ftx = "#ffffff" if enabled else "#777"
        self.cv.create_rectangle(x+3, y+3, x+w+3, y+h+3,
                                 fill="#222222", outline="")
        bg  = self.cv.create_rectangle(x, y, x+w, y+h,
                                       fill=col, outline="", width=0)
        tx  = self.cv.create_text(x+w//2, y+h//2, text=text,
                                  font=("Courier",11,"bold"), fill=ftx)
        if enabled:
            for item in (bg, tx):
                self.cv.tag_bind(item, "<Button-1>", lambda e, f=cmd: f())
                self.cv.tag_bind(item, "<Enter>",
                    lambda e, b=bg, c=color: self.cv.itemconfig(b, fill=self._lt(c)))
                self.cv.tag_bind(item, "<Leave>",
                    lambda e, b=bg, c=color: self.cv.itemconfig(b, fill=c))

    def _lt(self, h):
        try:
            r = min(255, int(h[1:3],16)+35)
            g = min(255, int(h[3:5],16)+35)
            b = min(255, int(h[5:7],16)+35)
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return h

    def _result_banner(self):
        cx = WIDTH//2
        cy = HEIGHT//2 - 5
        self.cv.create_rectangle(cx-270, cy-24, cx+270, cy+24,
                                 fill="#0d0d0d", outline=self.msg_col, width=1)
        self.cv.create_text(cx, cy, text=self.msg,
                            font=("Georgia",15,"bold"), fill=self.msg_col)

    def _prompt(self, txt):
        self.cv.create_text(WIDTH//2, HEIGHT//2-5, text=txt,
                            font=("Courier",12), fill="#888888")


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    Game(root)
    root.mainloop()