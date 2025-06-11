from matrizes import calcular_determinante, calcular_inversa, multiplicar_matrizes
import random

MAX_TENTATIVAS_BASE = 50
TOLERANCIA = 1e-8

def base_valida(matriz_A, base, m):
    if len(base) != m:
        return False
    B = [[matriz_A[i][j] for j in base] for i in range(m)]
    try:
        det = calcular_determinante(B)
        return abs(det) > TOLERANCIA
    except:
        return False

def executar_fase1(vetor_c, matriz_A, vetor_b, tipos_restricao):
    m = len(matriz_A)
    n = len(matriz_A[0])
    iteracao = 1

    print("\n=== INÍCIO FASE I ===")
    
    # Base inicial: variáveis artificiais (garante matriz identidade)
    #Caso A
    base = []
    for i in range(m):
        # Procura coluna com 1 na linha i e 0 nas outras (variável artificial)
        for j in range(n):
            coluna = [matriz_A[k][j] for k in range(m)]
            if abs(coluna[i] - 1) < TOLERANCIA and all(abs(coluna[k]) < TOLERANCIA for k in range(m) if k != i):
                base.append(j)
                break
    
    # Se não encontrou todas as variáveis artificiais, tenta as últimas colunas
    #Caso B
    if len(base) != m:
        base = [j for j in range(n) if j >= n - m]
    
    # Verifica se a base é válida
    if not base_valida(matriz_A, base, m):
        print("Não foi possível encontrar base inicial válida para Fase I")
        return None, None, "infactível"

    while iteracao <= MAX_TENTATIVAS_BASE:
        print(f"\n--- Iteração {iteracao} ---")
        print(f"Base atual: {base}")

        # Passo 1: Calcular solução básica
        B = [[matriz_A[i][j] for j in base] for i in range(m)]
        try:
            B_inv = calcular_inversa(B)
        except ValueError:
            print("Matriz básica singular. Tentando outra base...")
            # Tenta encontrar outra base válida
            for tentativa in range(1, MAX_TENTATIVAS_BASE):
                base_candidata = random.sample(range(n), m)
                if base_valida(matriz_A, base_candidata, m):
                    base = base_candidata
                    print(f"Nova base encontrada: {base}")
                    B_inv = calcular_inversa([[matriz_A[i][j] for j in base] for i in range(m)])
                    break
            else:
                print("Não foi possível encontrar base viável após várias tentativas")
                return None, None, "infactível"
            continue

        #x_B = B⁻¹ * b
        x_B = [sum(B_inv[i][k] * vetor_b[k] for k in range(m)) for i in range(m)]
        solucao = [0] * n
        for i, j in enumerate(base):
            solucao[j] = x_B[i]

        print(f"Solução básica: {[round(x, 4) for x in solucao]}")
        valor_objetivo = sum(vetor_c[j] * solucao[j] for j in range(n))
        print(f"Valor objetivo Fase I: {round(valor_objetivo, 4)}")

        # Passo 2: Calcular custos relativos
        c_B = [vetor_c[j] for j in base]
        lambda_ = [sum(c_B[k] * B_inv[k][i] for k in range(m)) for i in range(m)] #vetor multiplicador
        
        nao_base = [j for j in range(n) if j not in base]
        custos_relativos = {
            j: vetor_c[j] - sum(lambda_[i] * matriz_A[i][j] for i in range(m))
            for j in nao_base
        }

        print(f"Custos relativos: {[(j, round(cr, 4)) for j, cr in custos_relativos.items()]}")

        # Passo 3: Teste de otimalidade
        j_entra = min(custos_relativos.items(), key=lambda item: item[1])[0]
        if custos_relativos[j_entra] >= -TOLERANCIA:
            print("\nFase I concluída - Teste de otimalidade satisfeito")
            
            # Verifica se o valor objetivo é próximo de zero (problema factível)
            if abs(valor_objetivo) > TOLERANCIA:
                print(f"Valor objetivo Fase I = {round(valor_objetivo, 6)} (≠ 0). Problema infactível.")
                return None, None, "infactível"
            else:
                print(f"Valor objetivo Fase I = {round(valor_objetivo, 6)} (≈ 0). Problema factível.")

            
            # Remove variáveis artificiais da base
            artificiais_na_base = [j for j in base if j >= n - m]
            if artificiais_na_base:
                # Tenta substituir variáveis artificiais por variáveis originais
                for j_art in artificiais_na_base:
                    i = base.index(j_art)
                    # Procura variável não artificial para entrar na base
                    for j in range(n - m):  # Considera apenas variáveis originais
                        if j not in base and abs(matriz_A[i][j]) > TOLERANCIA:
                            base[i] = j
                            break
                
                # Verifica se ainda há artificiais na base
                if any(j >= n - m for j in base):
                    print("Não foi possível remover todas as variáveis artificiais. Problema pode ser infactível.")
                    return None, None, "infactível"
            
            print(f"Base para Fase II: {base}")
            return solucao[:n - m], base, "factível"

        # Passo 4: Calcular direção simplex
        y = [sum(B_inv[i][k] * matriz_A[k][j_entra] for k in range(m)) for i in range(m)]

        # Passo 5: Determinar variável que sai
        razoes = {}
        for i in range(m):
            if y[i] > TOLERANCIA:
                razoes[i] = x_B[i] / y[i]
        
        if not razoes:
            print("Problema ilimitado na Fase I")
            return None, None, "ilimitado"
        
        # Prioriza saída de variáveis artificiais
        i_sai_candidatos = [i for i in razoes if base[i] >= n - m]  #artificiais
        if not i_sai_candidatos:
            i_sai_candidatos = list(razoes.keys())
        
        i_sai = min(i_sai_candidatos, key=lambda i: razoes[i])
        j_sai = base[i_sai]

        print(f"Variável que entra: x{j_entra}, que sai: x{j_sai}")

        # Passo 6: Atualizar base
        base[i_sai] = j_entra
        iteracao += 1

    print("Número máximo de iterações na Fase I atingido")
    return None, None, "infactível"

def executar_fase2(vetor_c, matriz_A, vetor_b, base_inicial, tipos_restricao):
    m = len(matriz_A)
    n = len(matriz_A[0])
    iteracao = 1
    base = base_inicial.copy()

    print("\n=== INÍCIO FASE II ===")

    while iteracao <= MAX_TENTATIVAS_BASE:
        print(f"\n--- Iteração {iteracao} ---")
        print(f"Base atual: {base}")

        # Passo 1: Calcular solução básica
        B = [[matriz_A[i][j] for j in base] for i in range(m)]
        try:
            B_inv = calcular_inversa(B)
        except ValueError:
            print("Matriz básica singular. Tentando outra base...")
            # Tenta encontrar outra base válida
            for tentativa in range(1, MAX_TENTATIVAS_BASE):
                base_candidata = random.sample(range(n), m)
                if base_valida(matriz_A, base_candidata, m):
                    base = base_candidata
                    print(f"Nova base encontrada: {base}")
                    B_inv = calcular_inversa([[matriz_A[i][j] for j in base] for i in range(m)])
                    break
            else:
                print("Não foi possível encontrar base viável após várias tentativas")
                return None, None, "erro"
            continue

        x_B = [sum(B_inv[i][k] * vetor_b[k] for k in range(m)) for i in range(m)]
        solucao = [0] * n
        for i, j in enumerate(base):
            solucao[j] = x_B[i]

        print(f"Solução básica: {[round(x, 4) for x in solucao]}")
        valor_objetivo = sum(vetor_c[j] * solucao[j] for j in range(n))
        print(f"Valor objetivo atual: {round(valor_objetivo, 4)}")

        # Passo 2: Calcular custos relativos
        c_B = [vetor_c[j] for j in base]
        lambda_ = [sum(c_B[k] * B_inv[k][i] for k in range(m)) for i in range(m)]
        
        nao_base = [j for j in range(n) if j not in base]
        custos_relativos = {
            j: vetor_c[j] - sum(lambda_[i] * matriz_A[i][j] for i in range(m))
            for j in nao_base
        }

        print(f"Custos relativos: {[(j, round(cr, 4)) for j, cr in custos_relativos.items()]}")

        # Passo 3: Teste de otimalidade
        j_entra = min(custos_relativos.items(), key=lambda item: item[1])[0]
        if custos_relativos[j_entra] >= -TOLERANCIA:
            print("\nSolução ótima encontrada!")
            return solucao, valor_objetivo, "ótimo"

        # Passo 4: Calcular direção simplex
        y = [sum(B_inv[i][k] * matriz_A[k][j_entra] for k in range(m)) for i in range(m)]

        # Passo 5: Determinar variável que sai
        razoes = {}
        for i in range(m):
            if y[i] > TOLERANCIA:
                razoes[i] = x_B[i] / y[i]
        
        if not razoes:
            print("Problema ilimitado")
            return None, None, "ilimitado"
        
        i_sai = min(razoes.items(), key=lambda item: item[1])[0]
        j_sai = base[i_sai]

        print(f"Variável que entra: x{j_entra}, que sai: x{j_sai}")

        # Passo 6: Atualizar base
        base[i_sai] = j_entra
        iteracao += 1

    print("Número máximo de iterações na Fase II atingido")
    return None, None, "erro"

def adicionar_variaveis_artificiais(matriz_A, vetor_b, vetor_c, tipos_restricao):
    m = len(matriz_A)
    n_original = len(matriz_A[0])
    
    # Matriz aumentada com variáveis artificiais
    matriz_A_art = [linha.copy() for linha in matriz_A]
    
    # Contador de variáveis artificiais adicionadas
    num_artificiais = 0
    indices_artificiais = []
    
    for i in range(m):
        if tipos_restricao[i] in [">=", "=", ">"]:
            # Adiciona variável artificial (coluna com 1 na linha i e 0 nas outras)
            for j in range(len(matriz_A_art)):
                if j == i:
                    matriz_A_art[j].append(1)
                else:
                    matriz_A_art[j].append(0)
            indices_artificiais.append(n_original + num_artificiais)
            num_artificiais += 1
        else:
            # Para restrições "<=", apenas estende com zeros
            for linha in matriz_A_art:
                linha.append(0)
    
    # Vetor de custos: 0 para originais e folgas, 1 para artificiais
    vetor_c_art = [0] * (len(matriz_A_art[0]) - num_artificiais) + [1] * num_artificiais
    
    return matriz_A_art, vetor_b, vetor_c_art, indices_artificiais