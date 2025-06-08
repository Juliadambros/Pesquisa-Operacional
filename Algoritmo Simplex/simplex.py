import random
from matrizes import calcular_determinante, calcular_inversa, multiplicar_matrizes, multiplicar_matriz_vetor

MAX_TENTATIVAS_BASE = 50
TOLERANCIA = 1e-8

def encontrar_base_viavel_aleatoria(matriz_A, vetor_b, m, n):
    tentativas = 0
    while tentativas < MAX_TENTATIVAS_BASE:
        base_candidata = random.sample(range(n), m)
        B = [[matriz_A[i][j] for j in base_candidata] for i in range(m)]

        if abs(calcular_determinante(B)) > TOLERANCIA:
            try:
                B_inv = calcular_inversa(B)
                xB = multiplicar_matriz_vetor(B_inv, vetor_b)

                if all(x >= -TOLERANCIA for x in xB):
                    return base_candidata
            except ZeroDivisionError:
                pass  # Ignora erros numéricos na inversa
        tentativas += 1
    return None

def base_valida(matriz_A, base, m):
    if len(base) != m:
        return False  # não é quadrada, logo inválida
    B = [[matriz_A[i][j] for j in base] for i in range(m)]
    det = calcular_determinante(B)
    return abs(det) > TOLERANCIA


def trocar_base(matriz_A, base_antiga, m, n):
    tentativas = 0
    while tentativas < MAX_TENTATIVAS_BASE:
        base_candidata = random.sample(range(n), m)
        if base_candidata != base_antiga and base_valida(matriz_A, base_candidata, m):
            return base_candidata
        tentativas += 1
    return None

def executar_fase1(vetor_c, matriz_A, vetor_b):
    m = len(matriz_A)
    n = len(matriz_A[0])
    iteracao = 1

    base = encontrar_base_viavel_aleatoria(matriz_A, vetor_b, m, n)

    if base is None:
        print("Não foi possível encontrar base viável aleatória para a Fase 1.")
        return None, None, "erro"

    nao_base = [j for j in range(n) if j not in base]

    print("\n*Fase 1*")

    while True:
        print(f"\nIteração {iteracao} - Fase 1")
        print(f"Base atual: {base}")

        B = [[matriz_A[i][j] for j in base] for i in range(m)]
        det_B = calcular_determinante(B)

        if abs(det_B) < TOLERANCIA:
            print("Determinante da base atual é zero. Tentando trocar a base...")
            base_antiga = base.copy()
            base = trocar_base(matriz_A, base_antiga, m, n)
            if base is None:
                print("Não foi possível encontrar nova base viável para continuar a Fase 1.")
                return None, None, "erro"
            nao_base = [j for j in range(n) if j not in base]
            continue

        B_inv = calcular_inversa(B)
        x_B = multiplicar_matrizes(B_inv, [[vetor_b[i]] for i in range(m)])
        solucao = [0] * n
        for i, j in enumerate(base):
            solucao[j] = x_B[i][0]

        print("Solução básica:", [solucao[j] for j in base])

        c_B = [vetor_c[j] for j in base]
        lambda_ = multiplicar_matrizes([c_B], B_inv)[0]

        custos_relativos = {}
        for j in nao_base:
            a_j = [matriz_A[i][j] for i in range(m)]
            c_j = vetor_c[j]
            custos_relativos[j] = c_j - sum(lambda_[i] * a_j[i] for i in range(m))

        if all(cr >= -TOLERANCIA for cr in custos_relativos.values()):
            print("Fase I concluída: solução básica factível encontrada.")
            return solucao, base, "factivel"

        j_entra = min(custos_relativos.items(), key=lambda item: item[1])[0]
        a_j = [[matriz_A[i][j_entra]] for i in range(m)]
        y = multiplicar_matrizes(B_inv, a_j)

        if all(y_i[0] <= 0 for y_i in y):
            print("Problema ilimitado na Fase 1.")
            return solucao, base, "ilimitado"

        razoes = {i: (x_B[i][0] / y[i][0] if y[i][0] > 0 else float('inf')) for i in range(m)}
        i_sai = min(razoes.items(), key=lambda item: item[1])[0]
        j_sai = base[i_sai]

        print(f"Variável que entra: x{j_entra}, que sai: x{j_sai}")

        base[i_sai] = j_entra
        nao_base = [j for j in range(n) if j not in base]

        iteracao += 1

def executar_fase2(vetor_c, matriz_A, vetor_b, base_inicial=None):
    m = len(matriz_A)
    n = len(matriz_A[0])
    iteracao = 1

    base = list(base_inicial) if base_inicial is not None else None

    if base is None or not base_valida(matriz_A, base, m):
        base = encontrar_base_viavel_aleatoria(matriz_A, vetor_b, m, n)
        if base is None:
            print("Não foi possível encontrar base viável para a Fase 2.")
            return None, None, "erro"

    nao_base = [j for j in range(n) if j not in base]

    print("\n*Fase 2*")

    while True:
        print(f"\nIteração {iteracao} - Fase 2")
        print(f"Base atual: {base}")

        B = [[matriz_A[i][j] for j in base] for i in range(m)]
        det_B = calcular_determinante(B)

        if abs(det_B) < TOLERANCIA:
            print("Determinante da base atual é zero. Tentando trocar a base...")
            base_antiga = base.copy()
            base = trocar_base(matriz_A, base_antiga, m, n)
            if base is None:
                print("Não foi possível encontrar nova base viável para continuar a Fase 2.")
                return None, None, "erro"
            nao_base = [j for j in range(n) if j not in base]
            continue

        B_inv = calcular_inversa(B)
        x_B = multiplicar_matrizes(B_inv, [[vetor_b[i]] for i in range(m)])
        solucao = [0] * n
        for i, j in enumerate(base):
            solucao[j] = x_B[i][0]

        print("Solução básica:", [solucao[j] for j in base])

        c_B = [vetor_c[j] for j in base]
        lambda_ = multiplicar_matrizes([c_B], B_inv)[0]

        custos_relativos = {}
        for j in nao_base:
            a_j = [matriz_A[i][j] for i in range(m)]
            c_j = vetor_c[j]
            custos_relativos[j] = c_j - sum(lambda_[i] * a_j[i] for i in range(m))

        if all(cr >= -TOLERANCIA for cr in custos_relativos.values()):
            print("Solução ótima encontrada.")
            valor_objetivo = sum(vetor_c[j] * solucao[j] for j in range(n))
            return solucao, valor_objetivo, "otimo"

        j_entra = min(custos_relativos.items(), key=lambda item: item[1])[0]
        a_j = [[matriz_A[i][j_entra]] for i in range(m)]
        y = multiplicar_matrizes(B_inv, a_j)

        if all(y_i[0] <= 0 for y_i in y):
            print("Problema ilimitado na Fase 2.")
            return solucao, 0, "ilimitado"

        razoes = {i: (x_B[i][0] / y[i][0] if y[i][0] > 0 else float('inf')) for i in range(m)}
        i_sai = min(razoes.items(), key=lambda item: item[1])[0]
        j_sai = base[i_sai]

        print(f"Variável que entra: x{j_entra}, que sai: x{j_sai}")

        base[i_sai] = j_entra
        nao_base = [j for j in range(n) if j not in base]

        iteracao += 1

def adicionar_variaveis_artificiais(matriz_A, vetor_b, vetor_c):
    m = len(matriz_A)
    n = len(matriz_A[0])

    matriz_A_art = [linha[:] for linha in matriz_A]  # Cópia da matriz A
    vetor_c_art = vetor_c + [0] * m

    for i in range(m):
        for j in range(m):
            matriz_A_art[j].append(1 if j == i else 0)

    base_inicial = list(range(n, n + m))

    return matriz_A_art, vetor_b[:], vetor_c_art, base_inicial

def verificar_artificiais_na_base(base, n_original):
    return any(ind >= n_original for ind in base)
