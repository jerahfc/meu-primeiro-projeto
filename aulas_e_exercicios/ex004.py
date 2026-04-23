# ===========================================================================
# EXPLORANDO MÉTODOS DE VALIDAÇÃO DE STRINGS (BOOLEANOS)
# ===========================================================================
# Esses métodos verificam o conteúdo da variável e retornam:
# True (Verdadeiro) ou False (Falso).
#
# .isspace()    -> A string contém APENAS espaços (ou tabs/quebras de linha)?
# .isnumeric()  -> A string contém APENAS números?
# .isalpha()    -> A string contém APENAS letras? (sem números ou símbolos)
# .isalnum()    -> A string é ALFANUMÉRICA? (letras e/ou números, sem símbolos)
# .isupper()    -> A string está inteira em letras MAIÚSCULAS?
# .islower()    -> A string está inteira em letras minúsculas?
# .istitle()    -> A string está "Capitalizada"? (Ex: "Curso De Python")

# A letra "a" usada antes do "a.isnumeric", "a.isalpha", é o que chamamos de objeto, ele pode mudar conforme o contexto.
# Todo objeto tem características e funcionalidades. Possuem atributos e métodos.
# Como estamos usando arênteses () depois de cada um deles, então estamos usando métodos.

# ===========================================================================

# Faça um programa que leia algo pelo teclado e mostre na tela o seu tipo primitivo e todas as informações possíveis sobre ele?

a = input("Digite algo: ")
print("O tipo primitivo desse valor é ", type(a))
print("Só tem espaços?", a.isspace())
print("É um número?", a.isnumeric())
print("É alfabético?", a.isalpha())
print("É alfanumérico?", a.isalnum())
print("Está em maiúsculas?", a.isupper())
print("Está em minúsculas?", a.islower())
print("Está capitalizada?", a.istitle())
