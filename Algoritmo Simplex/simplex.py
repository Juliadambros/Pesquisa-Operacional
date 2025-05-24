import random
from matrizes import calcular_determinante, calcular_inversa, multiplicar_matrizes

def escolher_base_valida(matriz_A, tamanho_base, tentativas_invalidas):
    colunas_totais = list(range(len(matriz_A[0])))
    tentativas = 0

    while True:
        base = tuple(sorted(random.sample(colunas_totais, tamanho_base)))
        if base in tentativas_invalidas:
            continue

        B = [[linha[i] for i in base] for linha in matriz_A]
        if len(B) != len(B[0]):
            tentativas_invalidas.add(base)
            continue

        det = calcular_determinante(B)
        print(f"Tentativa de base: {base}, Determinante = {det}")

        if det != 0:
            return base
        else:
            tentativas_invalidas.add(base)
            tentativas += 1
            if tentativas > 100:
                raise ValueError("Não foi possível encontrar uma base viável.")

# Resolve o sistema Bx = b  usando a inversa
def resolver_sistema(B, b):
    B_inv = calcular_inversa(B)
    x = multiplicar_matrizes(B_inv, [[bi] for bi in b])
    return [linha[0] for linha in x]

def simplex_fase_2(matriz_A, vetor_b, vetor_c, base_inicial):
    m = len(matriz_A)
    n = len(matriz_A[0])

    base = list(base_inicial)
    nao_base = [i for i in range(n) if i not in base]

    while True:
        B = [[linha[i] for i in base] for linha in matriz_A]
        N = [[linha[i] for i in nao_base] for linha in matriz_A]

        xB = resolver_sistema(B, vetor_b)
        print("\nFase 2 - Solução básica atual (xB):", xB)

        cB = [vetor_c[i] for i in base]
        B_inv = calcular_inversa(B)
        lambda_T = multiplicar_matrizes([cB], B_inv)[0]

        custos_relativos = []
        for j in nao_base:
            aj = [[linha[j]] for linha in matriz_A]
            lambdaT_aj = sum(lambda_T[i] * aj[i][0] for i in range(m))
            cj = vetor_c[j]
            custo_relativo = cj - lambdaT_aj
            custos_relativos.append((j, custo_relativo))

        print("Custos relativos:", custos_relativos)

        candidatos = [t for t in custos_relativos if t[1] < 0]
        if not candidatos:
            print("Solução ótima encontrada!")
            solucao = [0] * n
            for idx, b_idx in enumerate(base):
                solucao[b_idx] = xB[idx]
            return solucao

        k, _ = min(candidatos, key=lambda x: x[1])
        a_k = [[linha[k]] for linha in matriz_A]
        y = multiplicar_matrizes(B_inv, a_k)
        print("Direção simplex y:", [linha[0] for linha in y])

        if all(linha[0] <= 0 for linha in y):
            raise ValueError("Problema ilimitado (função objetivo tende ao infinito).")

        razoes = [(xB[i] / y[i][0], i) for i in range(m) if y[i][0] > 0]
        _, l = min(razoes)

        print(f"Variável que entra: x{k}, Variável que sai: x{base[l]}")
        base[l] = k
        nao_base = [i for i in range(n) if i not in base]

def simplex(matriz_A, vetor_b, vetor_c, tipos_restricao=None):
    m = len(matriz_A)
    n = len(matriz_A[0])

    if tipos_restricao is None:
        tipos_restricao = ["<="] * m

    precisa_fase1 = False
    for i in range(m):
        if tipos_restricao[i] in [">=", "="] or vetor_b[i] < 0:
            precisa_fase1 = True
            break


    if not precisa_fase1:
        print("\nFase 1 não necessária. Executando Fase 2 diretamente...")
        base_inicial = [n - m + i for i in range(m)]  # índices das variáveis de folga
        return simplex_fase_2(matriz_A, vetor_b, vetor_c, base_inicial)

    # Caso precise de Fase 1
    artificiais = []
    nova_A = []

    for i, linha in enumerate(matriz_A):
        nova_linha = linha[:]
        nova_linha += [0] * m
        if tipos_restricao[i] in [">=", "="]:
            nova_linha[n + i] = 1
            artificiais.append(n + i)
        nova_A.append(nova_linha)

    nova_c = vetor_c + [0] * m
    c_fase1 = vetor_c + [1 if i in artificiais else 0 for i in range(n, n + m)]

    print("\nExecutando Fase 1...")
    base_inicial = artificiais[:]
    solucao_fase1 = simplex_fase_2(nova_A, vetor_b, c_fase1, base_inicial)
    valor_fase1 = sum(solucao_fase1[i] for i in artificiais)

    if valor_fase1 > 1e-6:
        raise ValueError("Problema infactível (Fase 1 retornou valor positivo).")

    print("\nExecutando Fase 2...")
    matriz_sem_artificiais = [linha[:n] for linha in nova_A]
    return simplex_fase_2(matriz_sem_artificiais, vetor_b, vetor_c, base_inicial=[i for i in range(n) if i not in artificiais])