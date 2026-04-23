import tkinter as tk
from tkinter import font
import sys

# ── Constantes de cor e estilo ──────────────────────────────────────────────
BG        = "#0f0f1a"
CELL_BG   = "#1a1a2e"
CELL_HOV  = "#16213e"
BORDER    = "#0f3460"
X_COLOR   = "#e94560"
O_COLOR   = "#00d4ff"
TIE_COLOR = "#f0a500"
TEXT_FG   = "#e0e0e0"
BTN_BG    = "#0f3460"
BTN_HOV   = "#e94560"

# ── Lógica do jogo ───────────────────────────────────────────────────────────
class JogoDaVelha:
    LINHAS_VENCEDORAS = [
        (0,1,2),(3,4,5),(6,7,8),   # linhas
        (0,3,6),(1,4,7),(2,5,8),   # colunas
        (0,4,8),(2,4,6),           # diagonais
    ]

    def __init__(self):
        self.reiniciar()

    def reiniciar(self):
        self.tabuleiro   = [""] * 9
        self.jogador_atual = "X"
        self.terminado   = False
        self.vencedor    = None
        self.linha_vitoria = None

    def jogar(self, pos):
        if self.terminado or self.tabuleiro[pos]:
            return False
        self.tabuleiro[pos] = self.jogador_atual
        self._verificar_fim()
        if not self.terminado:
            self.jogador_atual = "O" if self.jogador_atual == "X" else "X"
        return True

    def _verificar_fim(self):
        for combo in self.LINHAS_VENCEDORAS:
            a, b, c = combo
            if (self.tabuleiro[a]
                    and self.tabuleiro[a] == self.tabuleiro[b] == self.tabuleiro[c]):
                self.vencedor    = self.tabuleiro[a]
                self.linha_vitoria = combo
                self.terminado   = True
                return
        if all(self.tabuleiro):
            self.terminado = True   # empate

# ── Interface gráfica ────────────────────────────────────────────────────────
class App:
    def __init__(self, root: tk.Tk):
        self.root  = root
        self.jogo  = JogoDaVelha()
        self.botoes: list[tk.Button] = []

        self._configurar_janela()
        self._construir_ui()
        self._atualizar_status()

    # ── Setup ──────────────────────────────────────────────────────────────
    def _configurar_janela(self):
        self.root.title("Jogo da Velha")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        # Centraliza na tela
        self.root.update_idletasks()
        w, h = 480, 600
        x = (self.root.winfo_screenwidth()  - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _construir_ui(self):
        # Fontes
        self.fnt_titulo  = font.Font(family="Courier New", size=22, weight="bold")
        self.fnt_celula  = font.Font(family="Courier New", size=40, weight="bold")
        self.fnt_status  = font.Font(family="Courier New", size=14)
        self.fnt_placar  = font.Font(family="Courier New", size=11)
        self.fnt_btn     = font.Font(family="Courier New", size=11, weight="bold")

        # Placar
        self.placar = {"X": 0, "Empate": 0, "O": 0}

        # ── Cabeçalho ──
        cabecalho = tk.Frame(self.root, bg=BG)
        cabecalho.pack(pady=(22, 4))

        tk.Label(cabecalho, text="✕ JOGO DA VELHA ○",
                 font=self.fnt_titulo, bg=BG, fg=TEXT_FG).pack()

        decoracao = tk.Frame(self.root, bg=BORDER, height=2, width=400)
        decoracao.pack(pady=4)

        # ── Placar ──
        placar_frame = tk.Frame(self.root, bg=BG)
        placar_frame.pack(pady=8)

        self.lbl_placar_x = tk.Label(
            placar_frame, text="X  0", font=self.fnt_placar,
            bg=BG, fg=X_COLOR, width=9, anchor="center")
        self.lbl_placar_x.grid(row=0, column=0, padx=8)

        tk.Label(placar_frame, text="·", font=self.fnt_placar,
                 bg=BG, fg=TEXT_FG).grid(row=0, column=1)

        self.lbl_placar_emp = tk.Label(
            placar_frame, text="EMP  0", font=self.fnt_placar,
            bg=BG, fg=TIE_COLOR, width=9, anchor="center")
        self.lbl_placar_emp.grid(row=0, column=2, padx=8)

        tk.Label(placar_frame, text="·", font=self.fnt_placar,
                 bg=BG, fg=TEXT_FG).grid(row=0, column=3)

        self.lbl_placar_o = tk.Label(
            placar_frame, text="O  0", font=self.fnt_placar,
            bg=BG, fg=O_COLOR, width=9, anchor="center")
        self.lbl_placar_o.grid(row=0, column=4, padx=8)

        # ── Status ──
        self.lbl_status = tk.Label(
            self.root, text="", font=self.fnt_status,
            bg=BG, fg=TEXT_FG, pady=6)
        self.lbl_status.pack()

        # ── Grade 3×3 ──
        grade = tk.Frame(self.root, bg=BORDER, padx=3, pady=3)
        grade.pack(pady=6)

        for i in range(9):
            btn = tk.Button(
                grade,
                text="", font=self.fnt_celula,
                width=3, height=1,
                bg=CELL_BG, fg=TEXT_FG,
                activebackground=CELL_HOV,
                relief="flat", bd=0,
                cursor="hand2",
                command=lambda pos=i: self._clicar(pos)
            )
            btn.grid(
                row=i // 3, column=i % 3,
                padx=3, pady=3,
                ipadx=14, ipady=14
            )
            btn.bind("<Enter>", lambda e, b=btn: self._hover_on(b))
            btn.bind("<Leave>", lambda e, b=btn: self._hover_off(b))
            self.botoes.append(btn)

        # ── Botão Reiniciar ──
        self.btn_reiniciar = tk.Button(
            self.root, text="[ REINICIAR ]",
            font=self.fnt_btn,
            bg=BTN_BG, fg=TEXT_FG,
            activebackground=BTN_HOV, activeforeground="#fff",
            relief="flat", bd=0, padx=20, pady=8,
            cursor="hand2",
            command=self._reiniciar
        )
        self.btn_reiniciar.pack(pady=16)
        self.btn_reiniciar.bind("<Enter>",
            lambda e: self.btn_reiniciar.config(bg=BTN_HOV))
        self.btn_reiniciar.bind("<Leave>",
            lambda e: self.btn_reiniciar.config(bg=BTN_BG))

        # Rodapé
        tk.Label(self.root, text="X sempre começa · dois jogadores · mesmo teclado",
                 font=font.Font(family="Courier New", size=9),
                 bg=BG, fg="#444466").pack(side="bottom", pady=6)

    # ── Eventos ───────────────────────────────────────────────────────────
    def _hover_on(self, btn: tk.Button):
        if btn["text"] == "":
            btn.config(bg=CELL_HOV)

    def _hover_off(self, btn: tk.Button):
        if btn["text"] == "":
            btn.config(bg=CELL_BG)

    def _clicar(self, pos: int):
        if not self.jogo.jogar(pos):
            return
        jogador = "X" if self.jogo.tabuleiro[pos] == "X" else "O"
        cor     = X_COLOR if jogador == "X" else O_COLOR
        self.botoes[pos].config(text=jogador, fg=cor, bg=CELL_BG)
        self._atualizar_status()

    def _reiniciar(self):
        self.jogo.reiniciar()
        for btn in self.botoes:
            btn.config(text="", fg=TEXT_FG, bg=CELL_BG)
        self._atualizar_status()

    # ── Status & Placar ───────────────────────────────────────────────────
    def _atualizar_status(self):
        j = self.jogo
        if j.terminado:
            if j.vencedor:
                cor  = X_COLOR if j.vencedor == "X" else O_COLOR
                msg  = f"  {j.vencedor} venceu!  🎉"
                self.placar[j.vencedor] += 1
                self._destacar_vitoria(j.linha_vitoria, cor)
            else:
                cor = TIE_COLOR
                msg = "  Empate!  🤝"
                self.placar["Empate"] += 1
            self.lbl_status.config(text=msg, fg=cor)
            self._bloquear_grade()
        else:
            cor = X_COLOR if j.jogador_atual == "X" else O_COLOR
            self.lbl_status.config(
                text=f"  Vez de: {j.jogador_atual}", fg=cor)

        self.lbl_placar_x.config(
            text=f"X  {self.placar['X']}")
        self.lbl_placar_emp.config(
            text=f"EMP  {self.placar['Empate']}")
        self.lbl_placar_o.config(
            text=f"O  {self.placar['O']}")

    def _destacar_vitoria(self, combo, cor):
        for i in combo:
            self.botoes[i].config(bg="#2a1a2e" if cor == X_COLOR else "#0a1f2e")

    def _bloquear_grade(self):
        for btn in self.botoes:
            btn.config(state="disabled",
                       disabledforeground=btn.cget("fg"))

# ── Entrada ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()