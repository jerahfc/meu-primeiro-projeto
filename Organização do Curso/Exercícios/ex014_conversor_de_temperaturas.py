# Escreva um programa que converta uma temperatura digitando em graus Celsius e converta para graus Fahrenheit.

celsius = float(input("Informe a temperatura em °C: "))
print(f"A temperatura de {celsius}°C corresponde a {(celsius * 9/5) + 32}°F")

# ------------OUTRA FORMA DE FAZER--------------------------------------------------------------------------------------

fahrenheit = (celsius * 9/5) + 32
print(f"A temperatura de {celsius}°C corresponde a {fahrenheit}°F")
