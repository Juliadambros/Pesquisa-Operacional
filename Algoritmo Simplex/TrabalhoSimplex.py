import random
import re

# Função para calcular o determinante de uma matriz quadrada (expansão de Laplace)
def calcular_determinante(matriz):
    if not matriz or any(len(linha) != len(matriz) for linha in matriz):
        raise ValueError("A matriz deve ser quadrada para calcular o determinante.")

    n = len(matriz)
    if n == 1:
        return matriz[0][0]
    if n == 2:
        return matriz[0][0] * matriz[1][1] - matriz[0][1] * matriz[1][0]

    det = 0
    for j in range(n):
        submatriz = []
        for linha in range(1, n):
            nova_linha = []
            for coluna in range(n):
                if coluna != j:
                    nova_linha.append(matriz[linha][coluna])
            submatriz.append(nova_linha)

        cofator = ((-1) ** j) * matriz[0][j] * calcular_determinante(submatriz)
        det += cofator

    return det

# Função para multiplicação de matrizes
def multiplicar_matrizes(A, B):
    n = len(A)
    m = len(B[0])
    p = len(B)

    if len(A[0]) != p:
        raise ValueError("O número de colunas de A deve ser igual ao número de linhas de B.")

    C = [[0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            for k in range(p):
                C[i][j] += A[i][k] * B[k][j]
    return C

# Função para calcular a inversa de uma matriz quadrada
def calcular_inversa(matriz):
    n = len(matriz)
    identidade = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    M = [linha[:] for linha in matriz]

    for i in range(n):
        if M[i][i] == 0:
            for j in range(i + 1, n):
                if M[j][i] != 0:
                    M[i], M[j] = M[j], M[i]
                    identidade[i], identidade[j] = identidade[j], identidade[i]
                    break

        divisor = M[i][i]
        for j in range(n):
            M[i][j] /= divisor
            identidade[i][j] /= divisor

        for k in range(n):
            if k != i:
                fator = M[k][i]
                for j in range(n):
                    M[k][j] -= M[i][j] * fator
                    identidade[k][j] -= identidade[i][j] * fator

    return identidade

# Função para separar a matriz básica B e não-básica N
def separar_B_N(matriz_A, num_restricoes):
    num_linhas = len(matriz_A)
    num_colunas = len(matriz_A[0])
    num_variaveis_originais = num_colunas - num_restricoes

    indices_possiveis = []
    for i in range(num_variaveis_originais, num_colunas):
        indices_possiveis.append(i)

    indices_B = []
    while len(indices_B) < num_restricoes:
        escolhido = random.choice(indices_possiveis)
        if escolhido not in indices_B:
            indices_B.append(escolhido)

    indices_N = []
    for i in range(num_colunas):
        if i not in indices_B:
            indices_N.append(i)

    B = []
    for i in range(num_linhas):
        linha = []
        for j in indices_B:
            linha.append(matriz_A[i][j])
        B.append(linha)

    N = []
    for i in range(num_linhas):
        linha = []
        for j in indices_N:
            linha.append(matriz_A[i][j])
        N.append(linha)

    return B, N, indices_B, indices_N

# Função para extrair os coeficientes da equação
def extrair_termos(expr):
    expr = expr.replace(" ", "").replace(",", ".")

    if re.search(r'[a-wy-zA-WY-Z]', expr):
        raise ValueError("Expressão contém variáveis inválidas. Use apenas 'x' seguido de número.")

    matches = re.findall(r'([+-]?\d*\.?\d*)(x\d+)', expr)

    termos = []
    for coef_str, var_str in matches:
        if coef_str in ['', '+']:
            coef = 1.0
        elif coef_str == '-':
            coef = -1.0
        else:
            coef = float(coef_str)
        var = int(var_str[1:])
        termos.append((coef, var))
    return termos

# Função para ler o arquivo de entrada e preparar as matrizes
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

        equacao = [0] * (quantidade_variaveis + variaveis_folga)
        for coef, var in partes:
            equacao[var - 1] = coef

        if operador == ">=":
            equacao.append(-1)
        elif operador == "<=":
            equacao.append(1)
        else:
            equacao.append(0)

        matriz_A.append(equacao)
        vetor_b.append(resultado)
        variaveis_folga += 1

    for linha in matriz_A:
        while len(linha) < quantidade_variaveis + variaveis_folga:
            linha.append(0)

    vetor_c.extend([0] * (len(matriz_A[0]) - len(vetor_c)))

    return matriz_A, vetor_b, vetor_c, tipo_otimizacao

# Função para verificar e preparar o problema para a Fase 1 ou 2
def preparar_fase_1(matriz_A, vetor_b, vetor_c, tipo_otimizacao):
    if tipo_otimizacao == "max":
        print("Transformando o problema de maximização para minimização...")
        vetor_c = [-coef for coef in vetor_c]  # Inverte os coeficientes da função objetivo

    for i in range(len(vetor_b)):
        if vetor_b[i] < 0:
            print(f"Valor b[{i}] é negativo. Multiplicando a restrição por -1...")
            matriz_A[i] = [-coef for coef in matriz_A[i]]
            vetor_b[i] = -vetor_b[i]

    # Verificar se há desigualdades ">=, >, =" que requerem a Fase I
    for linha in matriz_A:
        if linha[-1] != 0:
            print("Existem desigualdades que exigem a Fase I.")
            return True  # Requer Fase I

    print("Nenhuma restrição exige a Fase I. Podemos ir diretamente para a Fase II.")
    return False

# Função principal
def resolver_simplex(arquivo):
    matriz_A, vetor_b, vetor_c, tipo_otimizacao = ler_arquivo(arquivo)

    # Preparar para Fase 1 ou 2
    precisa_fase_1 = preparar_fase_1(matriz_A, vetor_b, vetor_c, tipo_otimizacao)

    if precisa_fase_1:
        print("Iniciando Fase 1...")
        resultado_fase1 = fase_1_simplex(matriz_A, vetor_b, vetor_c, tipo_otimizacao)
        if resultado_fase1 is None:
            print("Fim do processo: problema inviável.")
            return
        else:
            matriz_A, vetor_b, vetor_c, indices_B = resultado_fase1
    else:
        print("Iniciando Fase 2...")
        num_restricoes = len(matriz_A)
        num_variaveis = len(vetor_c)
        indices_B = list(range(num_variaveis - num_restricoes, num_variaveis))
    # Executar Fase 2
    fase_2_simplex(matriz_A, vetor_b, vetor_c, indices_B, tipo_otimizacao)

def fase_1_simplex(matriz_A, vetor_b, vetor_c, tipo_otimizacao):
    num_restricoes = len(matriz_A)
    num_variaveis = len(matriz_A[0])
    
    # Identificar as linhas que precisam de variáveis artificiais
    indices_artificiais = []
    for i in range(num_restricoes):
        if matriz_A[i][-1] != 1:  # só folga não resolve, ou é = ou >=
            indices_artificiais.append(i)
    
    # Adiciona variáveis artificiais
    for i in range(num_restricoes):
        for j in range(len(matriz_A)):
            if j == i:
                matriz_A[j].append(1 if i in indices_artificiais else 0)
            else:
                matriz_A[j].append(0)
    
    num_variaveis_totais = len(matriz_A[0])
    
    # Criar vetor de custo auxiliar (função objetivo da fase 1)
    vetor_c_aux = [0] * num_variaveis_totais
    for i in range(num_variaveis, num_variaveis_totais):
        vetor_c_aux[i] = 1  # Minimizar a soma das variáveis artificiais
    
    # Separar matriz básica B e não-básica N
    B, N, indices_B, indices_N = separar_B_N(matriz_A, num_restricoes)
    
    print("\n[FASE 1] Início da Fase 1")
    print("Matriz A com artificiais:")
    for linha in matriz_A:
        print(linha)
    print("Vetor b:", vetor_b)
    print("Vetor c auxiliar:", vetor_c_aux)

    iteracao = 0
    while True:
        iteracao += 1
        print(f"\nIteração {iteracao}:")
        
        B, N, indices_B, indices_N = separar_B_N(matriz_A, num_restricoes)
        B_inv = calcular_inversa(B)
        xB = multiplicar_matrizes(B_inv, [[bi] for bi in vetor_b])  # xB = B⁻¹b

        custo_B = [vetor_c_aux[i] for i in indices_B]
        custo_B_matriz = [[c] for c in custo_B]
        
        # c_B^T * B⁻¹
        yT = multiplicar_matrizes([custo_B], B_inv)
        
        # Calcula os custos reduzidos: c_N - y^T * N
        cN = [vetor_c_aux[i] for i in indices_N]
        yT_N = multiplicar_matrizes(yT, N)
        custo_reduzido = [cN[i] - yT_N[0][i] for i in range(len(indices_N))]

        print("Custo reduzido:", custo_reduzido)

        # Verifica otimalidade
        if all(cr >= 0 for cr in custo_reduzido):
            print("Solução ótima da Fase 1 encontrada.")
            valor_otimo = sum(vetor_c_aux[indices_B[i]] * xB[i][0] for i in range(len(indices_B)))
            print("Valor ótimo auxiliar:", valor_otimo)
            if valor_otimo > 0:
                print("Problema original é inviável.")
                return None
            else:
                print("Solução viável encontrada. Prosseguir para Fase 2.")
                return matriz_A, vetor_b, vetor_c, indices_B

        # Seleciona a variável que entra na base (mais negativo)
        q = custo_reduzido.index(min(custo_reduzido))
        coluna_entrada = [linha[q] for linha in N]
        
        # Direção simplex: d = B⁻¹ * a_q
        d = multiplicar_matrizes(B_inv, [[val] for val in coluna_entrada])
        
        print("Direção simplex:", [val[0] for val in d])

        # Determinar variável que sai da base
        razoes = []
        for i in range(len(d)):
            if d[i][0] > 0:
                razoes.append(xB[i][0] / d[i][0])
            else:
                razoes.append(float('inf'))
        
        if all(r == float('inf') for r in razoes):
            print("Problema ilimitado na Fase 1.")
            return None

        p = razoes.index(min(razoes))

        # Atualizar os índices da base
        indices_B[p], indices_N[q] = indices_N[q], indices_B[p]
        print(f"Variável que entra na base: x{indices_B[p]+1}")
        print(f"Variável que sai da base: x{indices_N[q]+1}")

def fase_2_simplex(matriz_A, vetor_b, vetor_c, indices_B, tipo_otimizacao):
    num_restricoes = len(matriz_A)
    num_variaveis = len(matriz_A[0])
    
    indices_N = [i for i in range(num_variaveis) if i not in indices_B]
    
    iteracao = 0
    while True:
        iteracao += 1
        print(f"\n[FASE 2] Iteração {iteracao}")
        
        # Montar matrizes B e N com base nos índices
        B = [[matriz_A[i][j] for j in indices_B] for i in range(num_restricoes)]
        N = [[matriz_A[i][j] for j in indices_N] for i in range(num_restricoes)]
        
        B_inv = calcular_inversa(B)
        xB = multiplicar_matrizes(B_inv, [[bi] for bi in vetor_b])

        custo_B = [vetor_c[i] for i in indices_B]
        yT = multiplicar_matrizes([custo_B], B_inv)

        cN = [vetor_c[i] for i in indices_N]
        yT_N = multiplicar_matrizes(yT, N)
        custo_reduzido = [cN[i] - yT_N[0][i] for i in range(len(indices_N))]

        print("Custo reduzido:", custo_reduzido)

        # Verifica condição de otimalidade
        if tipo_otimizacao == "min":
            otimo = all(cr >= 0 for cr in custo_reduzido)
        else:  # max
            otimo = all(cr <= 0 for cr in custo_reduzido)

        if otimo:
            print("Solução ótima encontrada na Fase 2!")
            solucao = [0] * num_variaveis
            for i, idx in enumerate(indices_B):
                solucao[idx] = xB[i][0]
            valor_otimo = sum(vetor_c[i] * solucao[i] for i in range(num_variaveis))
            print("Solução ótima:", solucao)
            print("Valor ótimo:", valor_otimo)
            return solucao, valor_otimo

        # Escolher variável para entrar na base
        if tipo_otimizacao == "min":
            q = custo_reduzido.index(min(custo_reduzido))
        else:
            q = custo_reduzido.index(max(custo_reduzido))

        coluna_entrada = [linha[q] for linha in N]
        d = multiplicar_matrizes(B_inv, [[val] for val in coluna_entrada])

        print("Direção simplex:", [round(val[0], 5) for val in d])

        razoes = []
        for i in range(len(d)):
            if d[i][0] > 0:
                razoes.append(xB[i][0] / d[i][0])
            else:
                razoes.append(float('inf'))

        if all(r == float('inf') for r in razoes):
            print("Problema ilimitado.")
            return None

        p = razoes.index(min(razoes))

        # Atualiza os índices
        indices_B[p], indices_N[q] = indices_N[q], indices_B[p]
        print(f"Variável que entra na base: x{indices_B[p]+1}")
        print(f"Variável que sai da base: x{indices_N[q]+1}")
