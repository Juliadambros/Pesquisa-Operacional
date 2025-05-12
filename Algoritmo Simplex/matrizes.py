def calcular_determinante(matriz):
    if not matriz or any(len(linha) != len(matriz) for linha in matriz):
        raise ValueError("A matriz deve ser quadrada para calcular o determinante.")

    n = len(matriz)
    if n == 1:
        return matriz[0][0]
    if n == 2:
        return matriz[0][0] * matriz[1][1] - matriz[0][1] * matriz[1][0]

    det = 0
    for j in range(n):
        submatriz = []
        for linha in range(1, n):
            nova_linha = []
            for coluna in range(n):
                if coluna != j:
                    nova_linha.append(matriz[linha][coluna])
            submatriz.append(nova_linha)

        cofator = ((-1) ** j) * matriz[0][j] * calcular_determinante(submatriz)
        det += cofator

    return det

def multiplicar_matrizes(A, B):
    if len(A[0]) != len(B):
        raise ValueError("Dimensões incompatíveis para multiplicação.")
    return [[sum(A[i][k] * B[k][j] for k in range(len(B)))
             for j in range(len(B[0]))] for i in range(len(A))]

def calcular_inversa(matriz):
    print("Determinante de B:", calcular_determinante(matriz))
    n = len(matriz)
    identidade = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    M = [linha[:] for linha in matriz]

    for i in range(n):
        if M[i][i] == 0:
            for j in range(i + 1, n):
                if M[j][i] != 0:
                    M[i], M[j] = M[j], M[i]
                    identidade[i], identidade[j] = identidade[j], identidade[i]
                    break

        divisor = M[i][i]
        for j in range(n):
            M[i][j] /= divisor
            identidade[i][j] /= divisor

        for k in range(n):
            if k != i:
                fator = M[k][i]
                for j in range(n):
                    M[k][j] -= M[i][j] * fator
                    identidade[k][j] -= identidade[i][j] * fator

    return identidade
