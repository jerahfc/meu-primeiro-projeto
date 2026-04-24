# =============================================================================================

# O sinal de igual junto == significa comparação de igualdade.
# Ele é usado para verificar se dois valores são iguais, retornando um resultado booleano...
# True → se forem iguais
# False → se forem diferentes

# Ex1: 

x = 10
y = 10

print(x == y)  # True

# Ex2:

x = 10
y = 5

print(x == y)  # False

# == → comparação (verifica igualdade)
# Diferente do sinal de igual sozinho = → atribuição (coloca um valor na variável)

# =============================================================================================
# OPERADORES ARITMÉTICOS PYTHON
# =============================================================================================

# +   -> Adição
# -   -> Subtração
# *   -> Multiplicação
# /   -> Divisão (resultado float)
# //  -> Divisão inteira
# %   -> Módulo (resto da divisão)
# **  -> Exponenciação

# =============================================================================================
# ORDEM DE PRECEDÊNCIA (PRIORIDADE)
# =============================================================================================

# 1. ()     -> Parênteses (sempre primeiro)
# 2. **     -> Exponenciação
# 3. +x, -x  -> Sinais unários (positivo e negativo)
# 4. *, /, //, %  -> Multiplicação, divisão, divisão inteira e módulo
# 5. +, -   -> Adição e subtração

# =============================================================================================
# DICA IMPORTANTE
# =============================================================================================

# Expressões são resolvidas da esquerda para a direita
# EXCETO quando a precedência manda o contrário

# Parênteses sempre podem mudar a ordem:
# exemplo: (2 + 3) * 4

# =============================================================================================

n1 = int(input("Digite um número: "))
n2 = int(input("Digite outro número: "))
s = n1 + n2
m = n1 * n2
d = n1 / n2
di = n1 // n2
e = n1 ** n2
print(f"A soma é: {s}, \n o produto é {m}, \n a divisão é {d:.3f}", end=" >>")
print(f"A divisão inteira é {di} e a potência é {e}")

# O operador end="" é usado para evitar a quebra de linha automática no final da impressão, permitindo que a próxima impressão continue na mesma linha.
# O operador :.3f é usado para formatar a saída da divisão, limitando o número de casas decimais a 3.
# O operador \n é usado para inserir uma quebra de linha, permitindo que cada resultado seja impresso em uma nova linha.
# O operador f antes da string indica que é uma f-string, permitindo a inclusão de expressões dentro das chaves {} para formatação e exibição dos resultados.
