def calculadora():
    print("=== Calculadora ===")
    print("Operações: + - * /")

    num1 = float(input("Digite o primeiro número: "))
    operacao = input("Digite a operação: ")
    num2 = float(input("Digite o segundo número: "))

    if operacao == "+":
        resultado = num1 + num2
    elif operacao == "-":
        resultado = num1 - num2
    elif operacao == "*":
        resultado = num1 * num2
    elif operacao == "/":
        if num2 == 0:
            print("Erro: divisão por zero!")
            return
        resultado = num1 / num2
    else:
        print("Operação inválida!")
        return

    print(f"Resultado: {num1} {operacao} {num2} = {resultado}")

calculadora()