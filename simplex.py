from matriz import calcular_inversa, multiplicar_matriz, separar_B_N, ler_arquivo
import random

def primeira_interacao(Basica, N, vetor_b, vetor_c, indices_B, indices_N):
    print("\n========== Início Simplex ==========")
    arquivo = "exercicio.txt"
    matriz_A, vetor_b, vetor_c, tipo_otimizacao = ler_arquivo(arquivo)
    num_restricoes = len(vetor_b)
    Basica, N, indices_B, indices_N = separar_B_N(matriz_A, num_restricoes)
    
    # Passo 1: x̂B = B⁻¹ * b
    B_inv = calcular_inversa(Basica)
    if B_inv is None:
        print("Matriz B não é invertível. Não é possível prosseguir.")
        return

    b_matrix = [[bi] for bi in vetor_b]
    xB = multiplicar_matriz(B_inv, b_matrix)
    print("\nSolução básica inicial x̂B:")
    for linha in xB:
        print(["{:.2f}".format(x) for x in linha])

    # x̂N = 0 (implícito)

    # Passo 2.1: λᵀ = cBᵀ * B⁻¹
    cB = [[vetor_c[i]] for i in indices_B]  # cB coluna
    cB_T = [[vetor_c[i] for i in indices_B]]  # cB linha
    lambda_T = multiplicar_matriz(cB_T, B_inv)
    print("\nMultiplicador simplex λᵀ:")
    print(["{:.2f}".format(x) for x in lambda_T[0]])

    # Passo 2.2: ĉN = cN - λᵀ * N
    cN = [[vetor_c[i]] for i in indices_N]
    N_matrix = [[linha[i] for i in indices_N] for linha in zip(*N)]  # Transposta para multiplicar
    lambda_N = multiplicar_matriz(lambda_T, N)
    c_hat_N = [[cN[i][0] - lambda_N[0][i]] for i in range(len(cN))]

    print("\nCustos reduzidos ĉN:")
    for i, val in enumerate(c_hat_N):
        print(f"ĉN{indices_N[i]+1} = {val[0]:.2f}")

    # Passo 2.3: Determinar variável que entra
    valores = [val[0] for val in c_hat_N]

    # Verifica se todos os custos reduzidos são >= 0
    if all(v >= 0 for v in valores):
        print("\nSolução ótima já encontrada na primeira interação!")
        return

    # Tenta encontrar uma variável de entrada com direção válida
    for index_entrada, custo in enumerate(valores):
        if custo < 0:
            var_entrada = indices_N[index_entrada]
            print(f"\nTentando variável x{var_entrada+1} como entrada (custo reduzido = {custo:.2f})")

            # Passo 4: y = B⁻¹ * aNk
            aNk = [[linha[index_entrada]] for linha in N]
            y = multiplicar_matriz(B_inv, aNk)

            print("Direção simplex y:")
            for linha in y:
                print(["{:.2f}".format(x) for x in linha])

            if any(linha[0] > 0 for linha in y):
                # Encontrou uma direção válida, continua com essa
                break
    else:
        print("\nProblema ilimitado: nenhuma variável de entrada resulta em direção viável (y > 0).")
        return


    # Passo 5: Verificar se o problema é ilimitado
    if all(linha[0] <= 0 for linha in y):
        print("\nProblema ilimitado: todas as entradas de y são <= 0.")
        return

    # Determinar variável que sai
    razoes = []
    for i in range(len(xB)):
        yi = y[i][0]
        if yi > 0:
            razoes.append((xB[i][0] / yi, i))
    _, index_saida = min(razoes)
    var_saida = indices_B[index_saida]
    print(f"\nVariável que sai da base: x{var_saida+1}")

    return var_entrada, var_saida
