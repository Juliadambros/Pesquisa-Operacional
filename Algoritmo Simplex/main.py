from leitura import ler_arquivo
from simplex import executar_fase1, executar_fase2, adicionar_variaveis_artificiais
from matrizes import calcular_determinante

def encontrar_base_viavel(matriz_A, m, n):
    """Tenta encontrar base inicial simples nas colunas da matriz A (identidade parcial)."""
    base_inicial = []
    for j in range(n):
        coluna = [matriz_A[i][j] for i in range(m)]
        if coluna.count(1) == 1 and coluna.count(0) == m - 1:
            base_inicial.append(j)
    # Garantir tamanho correto da base (máximo m colunas)
    return base_inicial[:m]

def main(arquivo):
    matriz_A, vetor_b, vetor_c, tipo_otimizacao, tipos_restricao = ler_arquivo(arquivo)

    print("\nMatriz A:")
    for linha in matriz_A:
        print(linha)

    print("\nVetor b:", vetor_b)
    print("Vetor c:", vetor_c)
    print("Tipo de problema:", tipo_otimizacao)

    if tipo_otimizacao == 'max':
        vetor_c = [-coef for coef in vetor_c]

    m = len(matriz_A)
    n = len(matriz_A[0])
    num_variaveis_originais = len(vetor_c)

    precisa_fase1 = False
    for i in range(m):
        if tipos_restricao[i] in [">=", ">", "="] or vetor_b[i] < 0:
            precisa_fase1 = True
            break

    if not precisa_fase1:
        print("\nFase 1 não necessária. Tentando executar Fase 2 diretamente...")

        base_inicial = encontrar_base_viavel(matriz_A, m, n)

        if len(base_inicial) != m:
            print("Não foi possível encontrar base viável simples. Executando Fase 1...")
            precisa_fase1 = True
        else:
            print(f"Base inicial encontrada para Fase 2: {base_inicial}")
            solucao_final, valor_objetivo, status_f2 = executar_fase2(vetor_c, matriz_A, vetor_b, base_inicial)

            if status_f2 == "ilimitado":
                print("Problema ilimitado! (não há solução ótima finita)")
                return

            print("\nSolução ótima encontrada:")
            print("x =", solucao_final[:num_variaveis_originais])
            print("Valor ótimo Z =", valor_objetivo)
            return

    if precisa_fase1:
        print("\nExecutando Fase 1 com variáveis artificiais...")
        matriz_A_art, vetor_b_art, vetor_c_art, base_inicial = adicionar_variaveis_artificiais(matriz_A, vetor_b, vetor_c)
        solucao_fase1, base_fase1, status_f1 = executar_fase1(vetor_c_art, matriz_A_art, vetor_b_art)

        if status_f1 == "infactível":
            print("Problema infactível! (não há solução viável)")
            return

        # Remove variáveis artificiais da base para preparar fase 2
        base_fase2 = [j for j in base_fase1 if j < n]
        folgas_disponiveis = [j for j in range(n) if j not in base_fase2]

        # Completar base para ter tamanho m (matriz quadrada e independente)
        folgas_disponiveis = [j for j in range(n) if j not in base_fase2]

        for candidato in folgas_disponiveis:
            tentativa_base = base_fase2 + [candidato]
            if len(tentativa_base) > m:
                break
            if len(tentativa_base) == m:  
                B_tentativa = [[matriz_A[i][j] for j in tentativa_base] for i in range(m)]
                det = calcular_determinante(B_tentativa)
                if abs(det) > 1e-8:
                    base_fase2 = tentativa_base
                    break 



        if len(base_fase2) < m:
            print("Base incompleta. Tentando executar Fase 2 com base parcial.")


        print(f"\nBase para Fase 2: {base_fase2} (tamanho {len(base_fase2)})")

        solucao_final, valor_objetivo, status_f2 = executar_fase2(vetor_c, matriz_A, vetor_b, base_fase2)

        if status_f2 == "ilimitado":
            print("Problema ilimitado! (não há solução ótima finita)")
            return

        print("\nSolução ótima encontrada:")
        print("x =", solucao_final[:num_variaveis_originais])
        print("Valor ótimo Z =", valor_objetivo)

if __name__ == '__main__':
    main("teste.txt")
