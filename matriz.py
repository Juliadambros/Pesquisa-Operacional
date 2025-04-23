import re
import random
from leitura import extrair_termos

# Função para ler o arquivo e processar os dados
def ler_arquivo(arquivo): 
    with open(arquivo, 'r') as arquivo:
        linhas = arquivo.readlines()

    primeira_linha = linhas[0].lower()
    tipo_otimizacao = "max" if "max" in primeira_linha else "min"
    funcao = primeira_linha.split('=')[1].strip()

    termos = extrair_termos(funcao)
    quantidade_variaveis = max(var for _, var in termos)
    vetor_c = [0] * quantidade_variaveis
    for coef, var in termos:
        vetor_c[var - 1] = coef

    matriz_A = []
    vetor_b = []
    variaveis_folga = 0

    for linha in linhas[1:]:
        linha = linha.strip()
        if not linha:
            continue

        if ">=" in linha:
            operador = ">="
            coefE, coefD = linha.split(">=")
        elif "<=" in linha:
            operador = "<="
            coefE, coefD = linha.split("<=")
        elif "=" in linha:
            operador = "="
            coefE, coefD = linha.split("=")
        else:
            continue

        partes = extrair_termos(coefE.strip())
        resultado = coefD.strip().replace(',', '.')  
        try:
            resultado = float(resultado)
        except ValueError:
            raise ValueError(f"Valor numérico inválido: {resultado}")

        # Monta a linha da matriz A
        equacao = [0] * (quantidade_variaveis + variaveis_folga)
        for coef, var in partes:
            equacao[var - 1] = coef

        # Adiciona a variável de folga
        if operador == ">=":
            equacao.append(-1)
        elif operador == "<=":
            equacao.append(1)
        else:
            equacao.append(0)

        matriz_A.append(equacao)
        vetor_b.append(resultado)
        variaveis_folga += 1

    # Preenche com zeros para alinhar o tamanho das colunas
    for linha in matriz_A:
        while len(linha) < quantidade_variaveis + variaveis_folga:
            linha.append(0)

    vetor_c.extend([0] * (len(matriz_A[0]) - len(vetor_c)))

    return matriz_A, vetor_b, vetor_c, tipo_otimizacao

# Função para calcular o determinante por Laplace
def calcular_determinante(matriz):
    if len(matriz) == 1:
        return matriz[0][0]
    if len(matriz) == 2:
        return matriz[0][0]*matriz[1][1] - matriz[0][1]*matriz[1][0]

    det = 0
    for j in range(len(matriz[0])):
        matrizB = [linha[:j] + linha[j+1:] for linha in matriz[1:]]
        cofator = ((-1) ** j) * matriz[0][j] * calcular_determinante(matrizB)
        det += cofator
    return det

# Função para calcular a inversa da matriz
def calcular_inversa(matriz):
    n = len(matriz)
    
    # Cria uma matriz identidade do mesmo tamanho
    identidade = [[float(i == j) for j in range(n)] for i in range(n)]

    # Faz uma cópia da matriz original para não modificar a entrada
    matriz_ampliada = [linha[:] + identidade[i][:] for i, linha in enumerate(matriz)]

    for i in range(n):
        # Verifica se o pivô é zero e tenta permutar linhas
        if matriz_ampliada[i][i] == 0:
            for k in range(i + 1, n):
                if matriz_ampliada[k][i] != 0:
                    matriz_ampliada[i], matriz_ampliada[k] = matriz_ampliada[k], matriz_ampliada[i]
                    break
            else:
                return None  # Não é invertível

        # Normaliza a linha do pivô
        fator = matriz_ampliada[i][i]
        for j in range(2 * n):
            matriz_ampliada[i][j] /= fator

        # Zera os outros elementos da coluna
        for k in range(n):
            if k != i:
                fator = matriz_ampliada[k][i]
                for j in range(2 * n):
                    matriz_ampliada[k][j] -= fator * matriz_ampliada[i][j]

    inversa = [linha[n:] for linha in matriz_ampliada]
    return inversa

# Função para separar as matrizes B e N
def separar_B_N(matriz_A, num_restricoes):
    num_colunas = len(matriz_A[0])
    num_variaveis_originais = num_colunas - num_restricoes

    matriz_transposta = list(map(list, zip(*matriz_A)))

    # Índices das variáveis básicas (aleatoriamente escolhidas entre as colunas restantes)
    indices_B = random.sample(range(num_variaveis_originais, num_colunas), num_restricoes)

    # Índices das variáveis não básicas (colunas restantes)
    indices_N = [i for i in range(num_variaveis_originais) if i not in indices_B]

    # Separar as colunas em B e N
    B = [list(matriz_transposta[i]) for i in indices_B]
    N = [list(matriz_transposta[i]) for i in indices_N]

    # Voltar para o formato original
    B = list(map(list, zip(*B)))
    N = list(map(list, zip(*N)))

    return B, N, indices_B, indices_N
