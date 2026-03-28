import tkinter as tk

# --- Constantes ---
TAMANHO = 70

COR_CLARA   = "#F0D9B5"
COR_ESCURA  = "#B58863"
COR_SEL     = "#7FC97F"
COR_MOV     = "#9FD49F"
COR_CAP     = "#E07070"
COR_VERM    = "#C0392B"
COR_VERM_B  = "#E74C3C"
COR_PRETA   = "#1A1A1A"
COR_PRETA_B = "#555555"
COR_BG      = "#1A1A2E"
COR_PAINEL  = "#16213E"
COR_TEXTO   = "#DCDCDC"
COR_SEC     = "#AAAAAA"
COR_BOTAO   = "#1F4068"
COR_BOTAO_H = "#0F3460"
COR_OURO    = "#F1C40F"
COR_AVISO   = "#E67E22"

VAZIO      = 0
VERMELHO_P = 1
PRETO_P    = 2
VERMELHO_D = 3
PRETO_D    = 4


def e_vermelho(p): return p in (VERMELHO_P, VERMELHO_D)
def e_preto(p):    return p in (PRETO_P, PRETO_D)
def e_dama(p):     return p in (VERMELHO_D, PRETO_D)
def pertence(p, t): return e_vermelho(p) if t == VERMELHO_P else e_preto(p)


def capturas(r, c, tabuleiro, turno):
    p = tabuleiro[r][c]
    if not p:
        return []
    dirs = [(-1,-1),(-1,1),(1,-1),(1,1)] if e_dama(p) else \
           [(-1,-1),(-1,1)] if e_vermelho(p) else [(1,-1),(1,1)]
    res = []
    for dr, dc in dirs:
        mr, mc = r+dr, c+dc
        lr, lc = r+dr*2, c+dc*2
        if 0 <= lr < 8 and 0 <= lc < 8 and tabuleiro[lr][lc] == VAZIO:
            meio = tabuleiro[mr][mc]
            if turno == VERMELHO_P and e_preto(meio):
                res.append((lr, lc, mr, mc))
            elif turno == PRETO_P and e_vermelho(meio):
                res.append((lr, lc, mr, mc))
    return res


def movimentos(r, c, tabuleiro):
    p = tabuleiro[r][c]
    if not p:
        return []
    dirs = [(-1,-1),(-1,1),(1,-1),(1,1)] if e_dama(p) else \
           [(-1,-1),(-1,1)] if e_vermelho(p) else [(1,-1),(1,1)]
    return [(r+dr, c+dc) for dr, dc in dirs
            if 0 <= r+dr < 8 and 0 <= c+dc < 8 and tabuleiro[r+dr][c+dc] == VAZIO]


def todas_capturas(turno, tabuleiro):
    res = []
    for r in range(8):
        for c in range(8):
            if tabuleiro[r][c] and pertence(tabuleiro[r][c], turno):
                for cap in capturas(r, c, tabuleiro, turno):
                    res.append(((r, c), cap))
    return res


def aplicar_movimento(r, c, nr, nc, tabuleiro, sobre=None):
    nb = [linha[:] for linha in tabuleiro]
    nb[nr][nc] = nb[r][c]
    nb[r][c] = VAZIO
    if sobre:
        nb[sobre[0]][sobre[1]] = VAZIO
    p = nb[nr][nc]
    if p == VERMELHO_P and nr == 0:
        nb[nr][nc] = VERMELHO_D
    if p == PRETO_P and nr == 7:
        nb[nr][nc] = PRETO_D
    return nb


def verificar_vitoria(tabuleiro, turno):
    vermelhos = sum(1 for r in range(8) for c in range(8) if e_vermelho(tabuleiro[r][c]))
    pretos    = sum(1 for r in range(8) for c in range(8) if e_preto(tabuleiro[r][c]))
    if vermelhos == 0: return PRETO_P
    if pretos    == 0: return VERMELHO_P
    caps = todas_capturas(turno, tabuleiro)
    if not caps:
        movs = [m for r in range(8) for c in range(8)
                if tabuleiro[r][c] and pertence(tabuleiro[r][c], turno)
                for m in movimentos(r, c, tabuleiro)]
        if not movs:
            return PRETO_P if turno == VERMELHO_P else VERMELHO_P
    return None


def novo_tabuleiro():
    tab = [[VAZIO]*8 for _ in range(8)]
    for r in range(3):
        for c in range(8):
            if (r+c) % 2 == 1:
                tab[r][c] = PRETO_P
    for r in range(5, 8):
        for c in range(8):
            if (r+c) % 2 == 1:
                tab[r][c] = VERMELHO_P
    return tab


class Damas:
    def __init__(self, root):
        self.root = root
        self.root.title("Jogo de Damas")
        self.root.configure(bg=COR_BG)
        self.root.resizable(False, False)
        self._build_ui()
        self.novo_jogo()

    def _build_ui(self):
        W = TAMANHO * 8

        # Painel superior
        self.painel_top = tk.Frame(self.root, bg=COR_PAINEL, height=60)
        self.painel_top.pack(fill="x")

        self.ind_canvas = tk.Canvas(self.painel_top, width=20, height=20,
                                    bg=COR_PAINEL, highlightthickness=0)
        self.ind_canvas.pack(side="left", padx=(16, 8), pady=20)

        self.lbl_turno = tk.Label(self.painel_top, text="", font=("Segoe UI", 13, "bold"),
                                   bg=COR_PAINEL, fg=COR_TEXTO)
        self.lbl_turno.pack(side="left")

        self.lbl_cap = tk.Label(self.painel_top, text="", font=("Segoe UI", 11),
                                 bg=COR_PAINEL, fg=COR_SEC)
        self.lbl_cap.pack(side="right", padx=16)

        # Mensagem
        self.lbl_msg = tk.Label(self.root, text="", font=("Segoe UI", 11),
                                 bg=COR_BG, fg=COR_AVISO, height=1)
        self.lbl_msg.pack(pady=(6, 0))

        # Canvas tabuleiro
        self.canvas = tk.Canvas(self.root, width=W, height=W,
                                 bg=COR_BG, highlightthickness=0)
        self.canvas.pack(padx=10, pady=6)
        self.canvas.bind("<Button-1>", self.clique)

        # Painel inferior
        self.painel_bot = tk.Frame(self.root, bg=COR_PAINEL)
        self.painel_bot.pack(fill="x")

        self.btn_novo = tk.Button(self.painel_bot, text="Nova Partida",
                                   font=("Segoe UI", 11), bg=COR_BOTAO, fg=COR_TEXTO,
                                   activebackground=COR_BOTAO_H, activeforeground=COR_TEXTO,
                                   relief="flat", padx=18, pady=8, cursor="hand2",
                                   command=self.novo_jogo)
        self.btn_novo.pack(side="left", padx=(20, 8), pady=10)

        self.btn_desfaz = tk.Button(self.painel_bot, text="Desfazer",
                                     font=("Segoe UI", 11), bg=COR_BOTAO, fg=COR_TEXTO,
                                     activebackground=COR_BOTAO_H, activeforeground=COR_TEXTO,
                                     relief="flat", padx=18, pady=8, cursor="hand2",
                                     command=self.desfazer)
        self.btn_desfaz.pack(side="left", pady=10)

    def novo_jogo(self):
        self.tabuleiro   = novo_tabuleiro()
        self.turno       = VERMELHO_P
        self.selecionado = None
        self.historico   = []
        self.cap_v       = 0
        self.cap_p       = 0
        self.mensagem    = ""
        self.vencedor    = None
        self.multi_cap   = None
        self.dicas_mov   = set()
        self.dicas_cap   = set()
        self._atualizar_painel()
        self._desenhar()

    def desfazer(self):
        if not self.historico:
            self.mensagem = "Nada para desfazer."
            self._atualizar_painel()
            return
        est = self.historico.pop()
        self.tabuleiro   = est["tab"]
        self.turno       = est["turno"]
        self.cap_v       = est["cap_v"]
        self.cap_p       = est["cap_p"]
        self.multi_cap   = est["multi"]
        self.selecionado = None
        self.vencedor    = None
        self.mensagem    = ""
        self.dicas_mov   = set()
        self.dicas_cap   = set()
        self._atualizar_painel()
        self._desenhar()

    def _salvar(self):
        self.historico.append({
            "tab":   [l[:] for l in self.tabuleiro],
            "turno": self.turno,
            "cap_v": self.cap_v,
            "cap_p": self.cap_p,
            "multi": self.multi_cap,
        })

    def _atualizar_painel(self):
        self.ind_canvas.delete("all")
        if self.vencedor:
            nome = "Vermelhas" if self.vencedor == VERMELHO_P else "Pretas"
            self.lbl_turno.config(text=f"Vencedor: {nome}! 🏆")
            cor = COR_VERM if self.vencedor == VERMELHO_P else COR_PRETA_B
            self.ind_canvas.create_oval(2, 2, 18, 18, fill=cor, outline=COR_OURO, width=2)
        else:
            nome = "Vermelhas" if self.turno == VERMELHO_P else "Pretas"
            self.lbl_turno.config(text=f"Vez das {nome}")
            cor = COR_VERM if self.turno == VERMELHO_P else COR_PRETA_B
            self.ind_canvas.create_oval(2, 2, 18, 18, fill=cor, outline="#888")

        self.lbl_cap.config(text=f"Verm. cap: {self.cap_p}   Pret. cap: {self.cap_v}")
        self.lbl_msg.config(text=self.mensagem)

    def _desenhar(self):
        self.canvas.delete("all")
        T = TAMANHO

        for r in range(8):
            for c in range(8):
                x1, y1 = c*T, r*T
                x2, y2 = x1+T, y1+T
                cor = COR_CLARA if (r+c) % 2 == 0 else COR_ESCURA
                if self.selecionado == (r, c):
                    cor = COR_SEL
                elif (r, c) in self.dicas_cap:
                    cor = COR_CAP
                elif (r, c) in self.dicas_mov:
                    cor = COR_MOV
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=cor, outline="")

        # Pontos de dica
        for (r, c) in self.dicas_mov:
            if self.tabuleiro[r][c] == VAZIO:
                cx, cy = c*T + T//2, r*T + T//2
                self.canvas.create_oval(cx-10, cy-10, cx+10, cy+10, fill=COR_SEL, outline="")

        for (r, c) in self.dicas_cap:
            if self.tabuleiro[r][c] == VAZIO:
                cx, cy = c*T + T//2, r*T + T//2
                self.canvas.create_oval(cx-12, cy-12, cx+12, cy+12, fill=COR_CAP, outline="")

        # Peças
        for r in range(8):
            for c in range(8):
                p = self.tabuleiro[r][c]
                if not p:
                    continue
                cx, cy = c*T + T//2, r*T + T//2
                raio = 28

                # Sombra
                self.canvas.create_oval(cx-raio+3, cy-raio+4,
                                        cx+raio+3, cy+raio+4,
                                        fill="#333333", outline="")

                cor_b = COR_VERM   if e_vermelho(p) else COR_PRETA
                cor_c = COR_VERM_B if e_vermelho(p) else COR_PRETA_B
                borda  = COR_SEL if self.selecionado == (r, c) else "#000000"
                borda_w = 3 if self.selecionado == (r, c) else 2

                self.canvas.create_oval(cx-raio, cy-raio, cx+raio, cy+raio,
                                        fill=cor_b, outline=borda, width=borda_w)
                self.canvas.create_oval(cx-raio+8, cy-raio+8,
                                        cx-raio+20, cy-raio+20,
                                        fill=cor_c, outline="")

                if e_dama(p):
                    self.canvas.create_text(cx, cy, text="D",
                                            font=("Segoe UI", 16, "bold"),
                                            fill=COR_OURO)

    def clique(self, evento):
        if self.vencedor:
            return
        T = TAMANHO
        c = evento.x // T
        r = evento.y // T
        if not (0 <= r < 8 and 0 <= c < 8):
            return

        p = self.tabuleiro[r][c]
        todas_caps = todas_capturas(self.turno, self.tabuleiro)

        if p and pertence(p, self.turno):
            if self.multi_cap and self.multi_cap != (r, c):
                self.mensagem = "Voce deve continuar capturando!"
                self._atualizar_painel()
                return
            self.selecionado = (r, c)
            self.mensagem = ""
            caps_sel = capturas(r, c, self.tabuleiro, self.turno)
            self.dicas_cap = {(lr, lc) for lr, lc, *_ in caps_sel}
            self.dicas_mov = set() if todas_caps else set(movimentos(r, c, self.tabuleiro))
            self._atualizar_painel()
            self._desenhar()
            return

        if not self.selecionado:
            return

        sr, sc = self.selecionado
        caps_sel = capturas(sr, sc, self.tabuleiro, self.turno)
        destino_caps = {(lr, lc): (mr, mc) for lr, lc, mr, mc in caps_sel}

        if todas_caps:
            if (r, c) in destino_caps:
                sobre = destino_caps[(r, c)]
                self._salvar()
                if e_vermelho(self.tabuleiro[sobre[0]][sobre[1]]):
                    self.cap_v += 1
                else:
                    self.cap_p += 1
                self.tabuleiro = aplicar_movimento(sr, sc, r, c, self.tabuleiro, sobre)
                prox = capturas(r, c, self.tabuleiro, self.turno)
                if prox:
                    self.multi_cap   = (r, c)
                    self.selecionado = (r, c)
                    self.dicas_cap   = {(lr, lc) for lr, lc, *_ in prox}
                    self.dicas_mov   = set()
                    self.mensagem    = "Continue capturando!"
                else:
                    self._fim_turno()
            else:
                self.mensagem = "Voce deve capturar!"
        else:
            movs = movimentos(sr, sc, self.tabuleiro)
            if (r, c) in movs:
                self._salvar()
                self.tabuleiro = aplicar_movimento(sr, sc, r, c, self.tabuleiro)
                self._fim_turno()
            else:
                self.selecionado = None
                self.dicas_mov   = set()
                self.dicas_cap   = set()

        self._atualizar_painel()
        self._desenhar()

    def _fim_turno(self):
        self.multi_cap   = None
        self.selecionado = None
        self.dicas_mov   = set()
        self.dicas_cap   = set()
        self.mensagem    = ""
        self.turno = PRETO_P if self.turno == VERMELHO_P else VERMELHO_P
        self.vencedor = verificar_vitoria(self.tabuleiro, self.turno)


if __name__ == "__main__":
    root = tk.Tk()
    Damas(root)
    root.mainloop()