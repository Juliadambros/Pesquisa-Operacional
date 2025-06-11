from leitura import ler_arquivo
from simplex import executar_fase1, executar_fase2, adicionar_variaveis_artificiais
from matrizes import calcular_determinante

# Garante base viável com variáveis originais após Fase 1
def reconstruir_base_viavel(matriz_A, m, n, base_fase1):
    base_nova = [j for j in base_fase1 if j < n]
    # Se ainda não tem m colunas, tenta completar com colunas viáveis
    if len(base_nova) < m:
        for j in range(n):
            if j not in base_nova:
                col = [matriz_A[i][j] for i in range(m)]
                if col.count(1) == 1 and col.count(0) == m - 1:
                    base_nova.append(j)
                if len(base_nova) == m:
                    break
    return base_nova

def encontrar_base_viavel(matriz_A, m, n):
    base_inicial = []
    for j in range(n):
        coluna = [matriz_A[i][j] for i in range(m)]
        if coluna.count(1) == 1 and coluna.count(0) == m - 1:   #Verifica se a coluna tem exatamente um "1" e o resto tudo "0"
            base_inicial.append(j)
    return base_inicial[:m]

def main(arquivo):
    matriz_A, vetor_b, vetor_c, tipo_otimizacao, tipos_restricao = ler_arquivo(arquivo)

    print("\nMatriz A:")
    for linha in matriz_A:
        print(linha)

    print("\nVetor b:", vetor_b)
    print("Vetor c:", vetor_c)
    print("Tipo de problema:", tipo_otimizacao)

    vetor_c_original = vetor_c.copy()
    if tipo_otimizacao == 'max':
        vetor_c = [-coef for coef in vetor_c]

    m = len(matriz_A)
    n = len(matriz_A[0])
    num_variaveis_originais = len(vetor_c)

    precisa_fase1 = any(
        tipos_restricao[i] in [">=", ">", "="] or vetor_b[i] < 0
        for i in range(m)
    )

    if not precisa_fase1:
        print("\nFase 1 não necessária. Tentando executar Fase 2 diretamente...")
        base_inicial = encontrar_base_viavel(matriz_A, m, n)

        if len(base_inicial) != m:
            print("Não foi possível encontrar base viável simples. Executando Fase 1...")
            precisa_fase1 = True
        else:
            print(f"Base inicial encontrada para Fase 2: {base_inicial}")
            solucao_final, valor_objetivo, status_f2 = executar_fase2(vetor_c, matriz_A, vetor_b, base_inicial, tipos_restricao)

            if status_f2 == "ilimitado":
                print("Problema ilimitado! (não há solução ótima finita)")
                return
            elif status_f2 == "erro":
                print("Erro durante a execução da Fase 2")
                return

            if tipo_otimizacao == 'max':
                valor_objetivo *= -1

            print("\nSolução ótima encontrada:")
            print("x =", solucao_final[:num_variaveis_originais])
            print("Valor ótimo Z =", valor_objetivo)
            return

    if precisa_fase1:
        print("\nExecutando Fase 1 com variáveis artificiais...")
        matriz_A_art, vetor_b_art, vetor_c_art, base_inicial = adicionar_variaveis_artificiais(matriz_A, vetor_b, vetor_c, tipos_restricao)
        
        print("\nMatriz A aumentada para Fase 1:")
        for linha in matriz_A_art:
            print(linha)
        print("Vetor c para Fase 1:", vetor_c_art)
        print("Base inicial para Fase 1:", base_inicial)

        solucao_fase1, base_fase1, status_f1 = executar_fase1(vetor_c_art, matriz_A_art, vetor_b_art, tipos_restricao)

        if status_f1 == "infactível":
            print("Problema infactível! (não há solução viável)")
            return
        elif status_f1 == "ilimitado":
            print("Problema ilimitado na Fase I")
            return

        # Prepara para Fase 2
        base_fase2 = reconstruir_base_viavel(matriz_A, m, n, base_fase1)

        print(f"\nBase para Fase 2: {base_fase2}")

        solucao_final, valor_objetivo, status_f2 = executar_fase2(vetor_c, matriz_A, vetor_b, base_fase2, tipos_restricao)

        if status_f2 == "ilimitado":
            print("Problema ilimitado! (não há solução ótima finita)")
            return
        elif status_f2 == "erro":
            print("Erro durante a execução da Fase 2")
            return

        if tipo_otimizacao == 'max':
            valor_objetivo *= -1

        print("\nSolução ótima encontrada:")
        print("x =", solucao_final[:num_variaveis_originais])
        print("Valor ótimo Z =", valor_objetivo)

if __name__ == '__main__':
    main("teste.txt")


