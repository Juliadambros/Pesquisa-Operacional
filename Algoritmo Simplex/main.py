from leitura import ler_arquivo
from simplex import executar_fase1, executar_fase2, adicionar_variaveis_artificiais

def main(arquivo):
    matriz_A, vetor_b, vetor_c, tipo_otimizacao, tipos_restricao = ler_arquivo(arquivo)

    print("\nMatriz A:")
    for linha in matriz_A:
        print(linha)

    print("\nVetor b:", vetor_b)
    print("Vetor c:", vetor_c)
    print("Tipo de problema:", tipo_otimizacao)

    # Se for maximização, converte para minimização
    if tipo_otimizacao == 'max':
        vetor_c = [-coef for coef in vetor_c]

    m = len(matriz_A)
    n = len(matriz_A[0])

    precisa_fase1 = False
    for i in range(m):
        if tipos_restricao[i] in [">=",">", "="] or vetor_b[i] < 0:
            precisa_fase1 = True
            break
    if not precisa_fase1:
        print("\nFase 1 não necessária. Executando Fase 2 diretamente...")

        # Tenta identificar base viável (colunas identidade)
        base_inicial = []
        for j in range(n):
            coluna = [matriz_A[i][j] for i in range(m)]
            if coluna.count(1) == 1 and coluna.count(0) == m - 1:
                base_inicial.append(j)

        if len(base_inicial) < m:
            print("Não foi possível encontrar base viável com variáveis de folga. Executando Fase 1...")
            precisa_fase1 = True
        else:
            solucao_final, valor_objetivo, status_f2 = executar_fase2(vetor_c, matriz_A, vetor_b, base_inicial)
            if status_f2 == "ilimitado":
                print("Problema ilimitado! (não há solução ótima finita)")
                return
            print("\nSolução ótima encontrada:")
            print("x =", solucao_final[:len(vetor_c)])
            print("Valor ótimo Z =", valor_objetivo)
            return

    if precisa_fase1:
        matriz_A_art, vetor_b_art, vetor_c_art, base_inicial = adicionar_variaveis_artificiais(matriz_A, vetor_b, vetor_c)
        solucao_fase1, base_fase1, status_f1 = executar_fase1(vetor_c_art, matriz_A_art, vetor_b_art)

        if status_f1 == "infactivel":
            print("Problema infactível! (não há solução viável)")
            return

        # Ajusta base para excluir variáveis artificiais
        base_fase2 = [j for j in base_fase1 if j < n]
        folgas_disponiveis = [j for j in range(n) if j not in base_fase2]
        while len(base_fase2) < m and folgas_disponiveis:
            base_fase2.append(folgas_disponiveis.pop(0))

        solucao_final, valor_objetivo, status_f2 = executar_fase2(vetor_c, matriz_A, vetor_b, base_fase2)
        if status_f2 == "ilimitado":
            print("Problema ilimitado! (não há solução ótima finita)")
            return

        print("\nSolução ótima encontrada:")
        print("x =", solucao_final[:len(vetor_c)])
        print("Valor ótimo Z =", valor_objetivo)

if __name__ == '__main__':
    main("teste.txt")
