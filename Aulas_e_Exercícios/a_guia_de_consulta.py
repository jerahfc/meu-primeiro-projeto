# ==========================================
# GUIA DE CONSULTA RÁPIDA - PYTHON
# ==========================================
# Tudo o que tem o '#' na frente é um comentário e o Python ignora.
# Use este arquivo para entender como os comandos funcionam na prática!

# --- 1. VARIÁVEIS E TIPOS DE DADOS ---
# Variáveis são 'caixinhas' que guardam informações na memória.
nome = "Jerah"                  # Texto (String / str). Sempre entre aspas.
quantidade_xicaras = 3          # Número Inteiro (Integer / int).
temperatura = 36.5              # Número Decimal (Float). Usa ponto, não vírgula.
estuda_filosofia = True         # Booleano (bool). Pode ser True (Verdadeiro) ou False (Falso).
vazio = None                    # NoneType. Representa o "nada" ou ausência de valor.

# --- 2. ESTRUTURAS DE DADOS ---
# Como organizar várias informações de uma vez.

# Lista (mutável): Uma fila de itens. Você pode adicionar ou tirar coisas depois.
metodos_cafe = ["cafeteira italiana", "coador de pano", "prensa francesa"]

# Tupla (imutável): Parecida com a lista, mas não pode ser alterada depois de criada.
coordenadas_limeira = (-22.56, -47.40) 

# Dicionário (Chave: Valor): Guarda informações associadas, como um cadastro.
perfil = {
    "nome": "Jerah",
    "cidade": "Limeira",
    "foco": "Python"
}

# --- 3. OPERADORES MATEMÁTICOS ---
soma = 10 + 5
subtracao = 10 - 5
multiplicacao = 10 * 5
divisao = 10 / 2         # Retorna 5.0 (na divisão, o Python sempre gera um float)
divisao_inteira = 10 // 3 # Retorna 3 (corta a parte decimal, não arredonda)
resto = 10 % 3           # Retorna 1 (pega apenas o que sobrou da divisão)
potencia = 2 ** 3        # 2 elevado a 3 (Retorna 8)

# --- 4. FUNÇÕES NATIVAS (Built-in) ---
# Ferramentas que já vêm prontas para usar.

# print(): Mostra mensagens ou resultados no terminal do VS Code.
print("Olá, " + nome + "! Bem-vindo aos exercícios.")

# type(): Descobre qual é o tipo de dado de uma variável.
print("O tipo da variável nome é:", type(nome))

# len(): Conta o tamanho de algo (itens em uma lista, letras em um texto).
total_metodos = len(metodos_cafe)
print("Temos", total_metodos, "métodos de fazer café na nossa lista.")

# input(): Pede para o usuário digitar algo. 
# (Está comentado abaixo para não travar a execução do código de exemplo)
# resposta = input("Qual o seu método favorito? ")

# --- 5. OPERADORES DE COMPARAÇÃO (Lógica) ---
# Eles sempre respondem com True (Verdadeiro) ou False (Falso).
igual = (5 == 5)         # True (Note que são dois sinais de igual para comparar)
diferente = (5 != 3)     # True
maior = (10 > 5)         # True
menor_igual = (5 <= 10)  # True

# --- 6. CONDICIONAIS (Tomadas de Decisão) ---
# if (se), elif (senão se), else (senão)
# IMPORTANTE: Note o espaço (identação) antes do print. Ele indica quem pertence a quem.
clima = "frio"

if clima == "frio":
    print("Tempo bom para um café quente.")
elif clima == "calor":
    print("Tempo bom para um café gelado.")
else:
    print("Clima indefinido, faça café mesmo assim.")

# --- 7. LOOPS (Laços de Repetição) ---

# FOR: Usado para percorrer itens em uma lista ou quando você sabe o número exato de repetições.
print("\nLendo a lista de métodos:") # O \n serve para pular uma linha
for metodo in metodos_cafe:
    print("- " + metodo)

# WHILE: Usado para repetir algo *enquanto* uma condição for verdadeira.
contador = 0
while contador < 3:
    print("Repetição número:", contador)
    contador = contador + 1  # Muito importante atualizar o contador para não criar um "loop infinito"!

# --- 8. FUNÇÕES (Criando seus próprios comandos) ---
# def: Define um bloco de código reutilizável.
def analisar_pensamento(ideia):
    # Tudo recuado faz parte da função
    if ideia == "":
        return "Nenhum pensamento fornecido."
    else:
        return "Analisando a ideia: " + ideia

# Para a função funcionar, você precisa "chamá-la":
resultado_analise = analisar_pensamento("Penso, logo existo.")
print(resultado_analise)

# --- 9. TRATAMENTO DE ERROS ---
# Tenta rodar um código que pode dar erro (crash), criando uma rota de fuga.
try:
    # Vai tentar fazer uma divisão impossível
    calculo_impossivel = 10 / 0
except ZeroDivisionError:
    print("Opa! O Python não consegue dividir números por zero.")

    # --- 10. FORMATAÇÃO DE TEXTOS COM F-STRINGS ---
# A forma moderna, rápida e recomendada de "injetar" variáveis em textos.
# Basta colocar um 'f' minúsculo antes da primeira aspa e escrever 
# a variável direto dentro das chaves { }.

marca_cafe = "Orfeu"
metodo_preparo = "Moka"
quantidade_xicaras = 3

# Exemplo básico: juntando texto e variáveis de forma natural
mensagem = f"Vou preparar {quantidade_xicaras} xícaras de café {marca_cafe} na {metodo_preparo}."
print(mensagem)


# Dica Extra 1: Formatação de Dinheiro / Casas Decimais
# O :.2f diz ao Python para mostrar o número (float) com exatamente 2 casas decimais.
preco_pacote = 28.9
mensagem_preco = f"O pacote de 250g custa R$ {preco_pacote:.2f}."
print(mensagem_preco) # Vai imprimir R$ 28.90 em vez de R$ 28.9


# Dica Extra 2: Operações Matemáticas Diretas
# Você pode fazer contas ou executar funções diretamente dentro das chaves!
mensagem_total = f"Se eu comprar 2 pacotes, vou gastar R$ {preco_pacote * 2:.2f}."
print(mensagem_total)