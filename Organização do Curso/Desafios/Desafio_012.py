# Faça um algoritmo que leia o preço de um produto e mostre, seu novo preço, com 5% de desconto.

preco_do_produto = float(input("Qual o preço do produto? R$"))
desconto = (preco_do_produto*5)/100
preco_do_produto_com_desconto = preco_do_produto - desconto
print(f"O produto com 5% de desconto custa R${preco_do_produto_com_desconto:.2f}")

# ------------OUTRA FORMA DE FAZER--------------------------------------------------------------------------------------

preco = float(input("Qual o preço do produto? R$"))
novo_preco = preco * 0.95
print(f"O produto com 5% de desconto custa R${novo_preco:.2f}")
