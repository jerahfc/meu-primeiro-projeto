# Crie um algoritmo que leia um número e mostre o seu dobro, triplo e raiz quadrada.

n = int(input("Digite um número: "))
print(f"O dobro de {n} é {n*2}, o triplo é {n*3} e a raiz quadrada é {n**(1/2):.2f}")

# ------------OUTRA FORMA DE FAZER--------------------------------------------------------------------------------------

n = int(input("Digite um número: "))
print(f"O dobro de {n} é {n*2}, o triplo é {n*3} e a raiz quadrada é {pow(n, (1/2)):.2f}")
