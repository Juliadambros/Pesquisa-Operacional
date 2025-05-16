from leitura import ler_arquivo
from simplex import fase_1_simplex, fase_2_simplex, preparar_fase_1

def resolver_simplex(arquivo):
    matriz_A, vetor_b, vetor_c, tipo_otimizacao = ler_arquivo(arquivo)
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

    fase_2_simplex(matriz_A, vetor_b, vetor_c, indices_B, tipo_otimizacao)

if __name__ == "__main__":
    resolver_simplex("Algoritmo Simplex/teste.txt")
