def multiplicar_matrizes(A, B):
    if len(A[0]) != len(B):
        raise ValueError("Número de colunas de A deve ser igual ao número de linhas de B.")
    
    resultado = [[0 for _ in range(len(B[0]))] for _ in range(len(A))]

    for i in range(len(A)):
        for j in range(len(B[0])):
            for k in range(len(B)):
                resultado[i][j] += A[i][k] * B[k][j]
    
    return resultado

A = [
    [1, 2],
    [3, 4]
]

B = [
    [5, 6],
    [7, 8]
]

resultado = multiplicar_matrizes(A, B)

for linha in resultado:
    print(linha)
