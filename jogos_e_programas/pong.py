import tkinter as tk
import random

# Configurações
LARGURA = 800
ALTURA = 600
VELOCIDADE_BOLA = 5
VELOCIDADE_RAQUETE = 20
TAMANHO_RAQUETE = 100
ESPESSURA_RAQUETE = 15

class Pong:
    def __init__(self, root):
        self.root = root
        self.root.title("Pong")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=LARGURA, height=ALTURA, bg="black")
        self.canvas.pack()

        self.pontos_jogador = 0
        self.pontos_cpu = 0
        self.rodando = False
        self.pausado = False

        self._criar_elementos()
        self._bind_teclas()
        self._tela_inicial()

    def _criar_elementos(self):
        # Linha central pontilhada
        for y in range(0, ALTURA, 20):
            self.canvas.create_line(LARGURA // 2, y, LARGURA // 2, y + 10,
                                    fill="#444444", width=2, tags="linha_central")

        # Placar
        self.texto_cpu = self.canvas.create_text(
            LARGURA // 4, 40, text="0", fill="white", font=("Courier", 48, "bold"))
        self.texto_jogador = self.canvas.create_text(
            3 * LARGURA // 4, 40, text="0", fill="white", font=("Courier", 48, "bold"))

        # Raquete CPU (esquerda)
        self.raquete_cpu = self.canvas.create_rectangle(
            20, ALTURA // 2 - TAMANHO_RAQUETE // 2,
            20 + ESPESSURA_RAQUETE, ALTURA // 2 + TAMANHO_RAQUETE // 2,
            fill="white", tags="raquete_cpu")

        # Raquete Jogador (direita)
        self.raquete_jogador = self.canvas.create_rectangle(
            LARGURA - 20 - ESPESSURA_RAQUETE, ALTURA // 2 - TAMANHO_RAQUETE // 2,
            LARGURA - 20, ALTURA // 2 + TAMANHO_RAQUETE // 2,
            fill="white", tags="raquete_jogador")

        # Bola
        self.bola = self.canvas.create_oval(
            LARGURA // 2 - 10, ALTURA // 2 - 10,
            LARGURA // 2 + 10, ALTURA // 2 + 10,
            fill="white", tags="bola")

        # Texto de mensagem central
        self.texto_mensagem = self.canvas.create_text(
            LARGURA // 2, ALTURA // 2 + 60,
            text="", fill="white", font=("Courier", 18))

    def _tela_inicial(self):
        self.canvas.itemconfig(self.texto_mensagem,
            text="Pressione ENTER para começar\n← ↑ ↓ → ou W/S para mover | P para pausar")
        self._resetar_bola()

    def _bind_teclas(self):
        self.root.bind("<Up>", lambda e: self._mover_jogador(-VELOCIDADE_RAQUETE))
        self.root.bind("<Down>", lambda e: self._mover_jogador(VELOCIDADE_RAQUETE))
        self.root.bind("w", lambda e: self._mover_jogador(-VELOCIDADE_RAQUETE))
        self.root.bind("W", lambda e: self._mover_jogador(-VELOCIDADE_RAQUETE))
        self.root.bind("s", lambda e: self._mover_jogador(VELOCIDADE_RAQUETE))
        self.root.bind("S", lambda e: self._mover_jogador(VELOCIDADE_RAQUETE))
        self.root.bind("<Return>", self._iniciar)
        self.root.bind("p", self._pausar)
        self.root.bind("P", self._pausar)

    def _mover_jogador(self, dy):
        coords = self.canvas.coords(self.raquete_jogador)
        if dy < 0 and coords[1] > 0:
            self.canvas.move(self.raquete_jogador, 0, dy)
        elif dy > 0 and coords[3] < ALTURA:
            self.canvas.move(self.raquete_jogador, 0, dy)

    def _resetar_bola(self):
        self.canvas.coords(self.bola,
            LARGURA // 2 - 10, ALTURA // 2 - 10,
            LARGURA // 2 + 10, ALTURA // 2 + 10)
        angulo = random.choice([-1, 1])
        vertical = random.uniform(-0.7, 0.7)
        self.bola_dx = VELOCIDADE_BOLA * angulo
        self.bola_dy = VELOCIDADE_BOLA * vertical

    def _iniciar(self, event=None):
        if not self.rodando:
            self.rodando = True
            self.canvas.itemconfig(self.texto_mensagem, text="")
            self._loop()

    def _pausar(self, event=None):
        if not self.rodando:
            return
        self.pausado = not self.pausado
        if self.pausado:
            self.canvas.itemconfig(self.texto_mensagem, text="⏸ PAUSADO — pressione P para continuar")
        else:
            self.canvas.itemconfig(self.texto_mensagem, text="")
            self._loop()

    def _loop(self):
        if not self.rodando or self.pausado:
            return

        self.canvas.move(self.bola, self.bola_dx, self.bola_dy)
        coords_bola = self.canvas.coords(self.bola)

        # Rebater nas paredes (topo/baixo)
        if coords_bola[1] <= 0:
            self.bola_dy = abs(self.bola_dy)
        if coords_bola[3] >= ALTURA:
            self.bola_dy = -abs(self.bola_dy)

        # Colisão com raquete do jogador
        coords_rj = self.canvas.coords(self.raquete_jogador)
        if (coords_bola[2] >= coords_rj[0] and
                coords_bola[0] <= coords_rj[2] and
                coords_bola[3] >= coords_rj[1] and
                coords_bola[1] <= coords_rj[3]):
            self.bola_dx = -abs(self.bola_dx) * 1.05
            centro_raquete = (coords_rj[1] + coords_rj[3]) / 2
            self.bola_dy = (coords_bola[1] + 10 - centro_raquete) / (TAMANHO_RAQUETE / 2) * VELOCIDADE_BOLA

        # Colisão com raquete da CPU
        coords_rc = self.canvas.coords(self.raquete_cpu)
        if (coords_bola[0] <= coords_rc[2] and
                coords_bola[2] >= coords_rc[0] and
                coords_bola[3] >= coords_rc[1] and
                coords_bola[1] <= coords_rc[3]):
            self.bola_dx = abs(self.bola_dx) * 1.05
            centro_raquete = (coords_rc[1] + coords_rc[3]) / 2
            self.bola_dy = (coords_bola[1] + 10 - centro_raquete) / (TAMANHO_RAQUETE / 2) * VELOCIDADE_BOLA

        # Limitar velocidade máxima
        velocidade_max = 15
        if abs(self.bola_dx) > velocidade_max:
            self.bola_dx = velocidade_max * (1 if self.bola_dx > 0 else -1)

        # IA da CPU
        centro_bola = (coords_bola[1] + coords_bola[3]) / 2
        centro_cpu = (coords_rc[1] + coords_rc[3]) / 2
        if centro_bola > centro_cpu + 5 and coords_rc[3] < ALTURA:
            self.canvas.move(self.raquete_cpu, 0, min(6, centro_bola - centro_cpu))
        elif centro_bola < centro_cpu - 5 and coords_rc[1] > 0:
            self.canvas.move(self.raquete_cpu, 0, max(-6, centro_bola - centro_cpu))

        # Ponto para o jogador (bola saiu pela esquerda)
        if coords_bola[0] <= 0:
            self.pontos_jogador += 1
            self.canvas.itemconfig(self.texto_jogador, text=str(self.pontos_jogador))
            self._ponto()
            return

        # Ponto para a CPU (bola saiu pela direita)
        if coords_bola[2] >= LARGURA:
            self.pontos_cpu += 1
            self.canvas.itemconfig(self.texto_cpu, text=str(self.pontos_cpu))
            self._ponto()
            return

        self.root.after(16, self._loop)  # ~60 FPS

    def _ponto(self):
        self.rodando = False
        self._resetar_bola()
        self.canvas.itemconfig(self.texto_mensagem, text="Pressione ENTER para continuar")

if __name__ == "__main__":
    root = tk.Tk()
    jogo = Pong(root)
    root.mainloop()