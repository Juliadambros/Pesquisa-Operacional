# main.py
from leitura import ler_arquivo
from simplex import simplex

def resolver_simplex(arquivo):
    matriz_A, vetor_b, vetor_c, tipo_otimizacao, tipos_restricao = ler_arquivo(arquivo)

    print("\n--- Dados do problema ---")
    print(f"Tipo de otimização: {tipo_otimizacao.upper()}")
    print("\nMatriz A:")
    for linha in matriz_A:
        print("  ", ["{:+.3f}".format(x) for x in linha])
    print("\nVetor b:")
    print("  ", ["{:+.3f}".format(x) for x in vetor_b])
    print("\nVetor c (função objetivo):")
    print("  ", ["{:+.3f}".format(x) for x in vetor_c])
    print("Tipos de restrição:")
    print(tipos_restricao)
    print("-------------------------\n")

    # Transforma max em min, se necessário
    if tipo_otimizacao == "max":
        vetor_c = [-c for c in vetor_c]

    try:
        solucao = simplex(matriz_A, vetor_b, vetor_c)
        print("\n--- Resultado final ---")
        print("Solução ótima (valores das variáveis):")
        for i, val in enumerate(solucao):
            if val < 0:
                val = 0  # Garante que a solução não tenha negativos
            print(f"x{i+1} = {val:.4f}")
        valor_objetivo = sum(solucao[i] * vetor_c[i] for i in range(len(vetor_c)))
        print(f"Valor ótimo da função objetivo: {valor_objetivo:.4f}")
        print("------------------------")
    except Exception as e:
        print("Erro:", e)

if __name__ == "__main__":
    resolver_simplex("teste.txt")
