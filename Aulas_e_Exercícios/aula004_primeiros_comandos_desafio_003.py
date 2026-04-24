#------------DESAFIO_003 PARTE LIMITADA-----------------------------------------------------------------------
# Crie um script Python que leia dois números e tente mostrar a soma entre eles.

número01 = input("Digite o primeiro número ")
número02 = input("Digite o segundo número ")
s = número01 + número02
print("A soma é,", s)

# Nesse caso, o sinal de "+" não está cumprindo a função adição, e sim de concatenação. Ele une os dois números sem somar, isso acontece no python porque não usamos os tipos primitivos.

# Jeito correto de fazer o Desafio 003:
#------------DESAFIO_003 PARTE CORRETA COM TIPOS PRIMITIVOS DA AULA 006-----------------------------------------------------------------------

n1 = int(input("Digite o primeiro número "))
n2 = int(input("Digite o segundo número "))
s = n1 + n2
print(f"A soma de {n1} e {n2} é igual a {s}")

# O operador f antes da string indica que é uma f-string, permitindo a inclusão de expressões dentro das chaves {} para formatação e exibição dos resultados.
