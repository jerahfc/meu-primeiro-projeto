# Faça um algoritmo que leia o salário de um funcionário e mostre seu novo salário, com 15% de aumento.

salario = float(input("Qual o seu salário? R$"))
aumento = (15/100) * salario
novo_salario = salario + aumento
print(f"Seu novo salário com aumento de 15% é de R${novo_salario:.2f}")

# ------------OUTRA FORMA DE FAZER--------------------------------------------------------------------------------------

salario = float(input("Qual o seu salário? R$"))
novo_salario = salario * 1.15
print(f"Seu novo salário com aumento de 15% é de R${novo_salario:.2f}")
