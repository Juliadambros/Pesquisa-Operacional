from matriz import ler_arquivo, calcular_determinante, calcular_inversa, separar_B_N
from leitura import extrair_termos
from simplex import primeira_interacao

def main():
    arquivo = "exercicio.txt"
    matriz_A, vetor_b, vetor_c, tipo_otimizacao = ler_arquivo(arquivo)

    print("Matriz A (com folgas):")
    for linha in matriz_A:
        print(linha)

    print("\nVetor b:")
    for coef in vetor_b:
        print(f"[{coef}]")

    print("Vetor C:", vetor_c)
    print("Tipo de otimização:", tipo_otimizacao)

    try:
        Bmatriz = matriz_A 

        det = calcular_determinante(Bmatriz)
        print("\nDeterminante (por Laplace):", det)

        # Verifica se a matriz é invertível
        if det != 0:
            inversa = calcular_inversa(Bmatriz)
            print("\nMatriz Inversa:")
            for linha in inversa:
                print(["{:.2f}".format(x) for x in linha])
        else:
            print("\nA matriz não possui inversa (determinante = 0).")

    except ValueError as e:
        print("Erro ao extrair submatriz quadrada:", e)

    num_restricoes = len(vetor_b)
    B, N, indices_B, indices_N = separar_B_N(matriz_A, num_restricoes)

    print("\nColunas escolhidas para as variáveis básicas (B):")
    print(", ".join([str(idx +1) for idx in indices_B]))

    print("\nColunas escolhidas para as variáveis não básicas (N):")
    print(", ".join([str(idx +1) for idx in indices_N]))

    
    print("\nMatriz B (variáveis básicas):")
    for linha in B:
        print(linha)

    print("\nMatriz N (variáveis não básicas):")
    for linha in N:
        print(linha)
    
    # Realizar a primeira interação do método Simplex
    primeira_interacao(B, N, vetor_b, vetor_c, indices_B, indices_N)

if __name__ == "__main__":
    main()
