import random
from matrizes import calcular_determinante, calcular_inversa, multiplicar_matrizes

def separar_B_N(matriz_A, num_restricoes):
    num_colunas = len(matriz_A[0])
    num_variaveis_originais = num_colunas - num_restricoes
    indices_possiveis = list(range(num_variaveis_originais, num_colunas))

    indices_B = random.sample(indices_possiveis, num_restricoes)
    indices_N = [i for i in range(num_colunas) if i not in indices_B]

    B = [[linha[j] for j in indices_B] for linha in matriz_A]
    N = [[linha[j] for j in indices_N] for linha in matriz_A]
    return B, N, indices_B, indices_N

# Função para verificar e preparar o problema para a Fase 1 ou 2
def preparar_fase_1(matriz_A, vetor_b, vetor_c, tipo_otimizacao):
    if tipo_otimizacao == "max":
        print("Transformando o problema de maximização para minimização...")
        vetor_c = [-coef for coef in vetor_c]  # Inverte os coeficientes da função objetivo
        print(vetor_c)

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

        # Tentativas para garantir base com determinante diferente de zero
        tentativas = 0
        while True:
            B, N, indices_B, indices_N = separar_B_N(matriz_A, num_restricoes)
            det_B = calcular_determinante(B)
            if det_B != 0:
                break
            else:
                tentativas += 1
                print(f"Tentativa {tentativas}: base com determinante zero. Sorteando nova base...")
                if tentativas > 100:
                    print("Não foi possível encontrar uma base viável com determinante diferente de zero.")
                    return None
                # embaralha os índices das colunas para nova base
                indices = list(range(len(matriz_A[0])))
                random.shuffle(indices)
                # reorganiza matriz_A de acordo com a nova ordem
                matriz_A = [[linha[i] for i in indices] for linha in matriz_A]
                vetor_c_aux = [vetor_c_aux[i] for i in indices]

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
    
    iteracao = 0
    while True:
        iteracao += 1
        print(f"\n[FASE 2] Iteração {iteracao}")

        # Atualiza os índices não básicos
        indices_N = [i for i in range(num_variaveis) if i not in indices_B]
        
        # Verificação do determinante da base
        tentativas = 0
        while True:
            B = [[matriz_A[i][j] for j in indices_B] for i in range(num_restricoes)]
            det_B = calcular_determinante(B)
            if det_B != 0:
                break
            else:
                tentativas += 1
                print(f"Tentativa {tentativas}: base com determinante zero. Sorteando nova base...")
                if tentativas > 100:
                    print("Não foi possível encontrar uma base viável com determinante diferente de zero.")
                    return None
                # Sorteia uma nova base viável
                todos_indices = list(range(num_variaveis))
                random.shuffle(todos_indices)
                indices_B = todos_indices[:num_restricoes]
                indices_N = [i for i in todos_indices if i not in indices_B]

        # Montar matrizes B e N
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