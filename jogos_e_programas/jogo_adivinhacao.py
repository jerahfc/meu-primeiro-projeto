import random

def jogar(maximo):
    secreto = random.randint(1, maximo)
    tentativas = 0

    print(f"\n🎯 Pensei em um número entre 1 e {maximo}. Tente adivinhar!\n")

    while True:
        try:
            chute = int(input("Seu chute: "))
        except ValueError:
            print("❌ Digite um número válido.\n")
            continue

        if chute < 1 or chute > maximo:
            print(f"❌ Digite um número entre 1 e {maximo}.\n")
            continue

        tentativas += 1

        if chute < secreto:
            print("⬆️  Muito baixo! Tente um número maior.\n")
        elif chute > secreto:
            print("⬇️  Muito alto! Tente um número menor.\n")
        else:
            print(f"🎉 Parabéns! Você acertou em {tentativas} tentativa{'s' if tentativas > 1 else ''}!\n")
            return tentativas

def menu_dificuldade():
    opcoes = {"1": 50, "2": 100, "3": 500}
    print("=" * 35)
    print("   🔢 JOGO DE ADIVINHAÇÃO")
    print("=" * 35)
    print("Escolha a dificuldade:")
    print("  [1] Fácil   — 1 a 50")
    print("  [2] Médio   — 1 a 100")
    print("  [3] Difícil — 1 a 500")
    print("-" * 35)
    while True:
        escolha = input("Opção (1/2/3): ").strip()
        if escolha in opcoes:
            return opcoes[escolha]
        print("❌ Opção inválida. Digite 1, 2 ou 3.")

def main():
    recorde = {}

    while True:
        maximo = menu_dificuldade()
        tentativas = jogar(maximo)

        # Atualiza recorde
        if maximo not in recorde or tentativas < recorde[maximo]:
            recorde[maximo] = tentativas
            print(f"🏆 Novo recorde para 1–{maximo}: {tentativas} tentativa{'s' if tentativas > 1 else ''}!")

        print(f"📊 Recorde atual (1–{maximo}): {recorde[maximo]} tentativa(s)\n")

        jogar_novamente = input("Jogar novamente? (s/n): ").strip().lower()
        if jogar_novamente != "s":
            print("\nAté a próxima! 👋\n")
            break

if __name__ == "__main__":
    main()