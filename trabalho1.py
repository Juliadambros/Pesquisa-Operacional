import re

def extrair_termos(expr):
    expr = expr.replace(" ", "").replace(",", ".")

    if re.search(r'[a-wy-zA-WY-Z]', expr):  # ignora 'x', mas bloqueia outras letras
        raise ValueError("Expressão contém variáveis inválidas. Use apenas 'x' seguido de número.")

    matches = re.findall(r'([+-]?\d*\.?\d*)(x\d+)', expr)

    termos = []
    for coef_str, var_str in matches:
        if coef_str in ['', '+']:
            coef = 1.0
        elif coef_str == '-':
            coef = -1.0
        else:
            coef = float(coef_str)
        var = int(var_str[1:])
        termos.append((coef, var))
    return termos

def ler_arquivo(arquivo): 
    with open(arquivo, 'r') as arquivo:
        linhas = arquivo.readlines()

    primeira_linha = linhas[0].lower()
    tipo_otimizacao = "max" if "max" in primeira_linha else "min"
    funcao = primeira_linha.split('=')[1].strip()

    termos = extrair_termos(funcao)
    quantidade_variaveis = max(var for _, var in termos)
    vetor_c = [0] * quantidade_variaveis
    for coef, var in termos:
        vetor_c[var - 1] = coef

    matriz_A = []
    vetor_b = []
    variaveis_folga = 0

    for linha in linhas[1:]:
        linha = linha.strip()
        if not linha:
            continue

        if ">=" in linha:
            operador = ">="
            coefE, coefD = linha.split(">=")
        elif "<=" in linha:
            operador = "<="
            coefE, coefD = linha.split("<=")
        elif "=" in linha:
            operador = "="
            coefE, coefD = linha.split("=")
        else:
            continue

        partes = extrair_termos(coefE.strip())
        resultado = coefD.strip().replace(',', '.')  
        try:
            resultado = float(resultado)
        except ValueError:
            raise ValueError(f"Valor numérico inválido: {resultado}")

        # Monta a linha da matriz A
        equacao = [0] * (quantidade_variaveis + variaveis_folga)
        for coef, var in partes:
            equacao[var - 1] = coef

        # Adiciona a variável de folga
        if operador == ">=":
            equacao.append(-1)
        elif operador == "<=":
            equacao.append(1)
        else:
            equacao.append(0)

        matriz_A.append(equacao)
        vetor_b.append(resultado)
        variaveis_folga += 1

    # Preenche com zeros para alinhar o tamanho das colunas
    for linha in matriz_A:
        while len(linha) < quantidade_variaveis + variaveis_folga:
            linha.append(0)

    vetor_c.extend([0] * (len(matriz_A[0]) - len(vetor_c)))

    return matriz_A, vetor_b, vetor_c, tipo_otimizacao

def determinante_laplace(matriz):
    if len(matriz) == 1:
        return matriz[0][0]
    if len(matriz) == 2:
        return matriz[0][0]*matriz[1][1] - matriz[0][1]*matriz[1][0]

    det = 0
    for j in range(len(matriz[0])):
        matrizB = [linha[:j] + linha[j+1:] for linha in matriz[1:]]
        cofator = ((-1) ** j) * matriz[0][j] * determinante_laplace(matrizB)
        det += cofator
    return det

def matriz_inversa(matriz):
    det = determinante_laplace(matriz)
    if det == 0:
        return None

    tamanho = len(matriz)
    cofatores = []
    for i in range(tamanho):
        linha_cofatores = []
        for j in range(tamanho):
            matrizB = [linha[:j] + linha[j+1:] for k, linha in enumerate(matriz) if k != i]
            cof = ((-1) ** (i + j)) * determinante_laplace(matrizB)
            linha_cofatores.append(cof)
        cofatores.append(linha_cofatores)

    # Transposta dos cofatores (matriz adjunta)
    cofatores_T = list(map(list, zip(*cofatores)))
    inversa = [[cofatores_T[i][j] / det for j in range(tamanho)] for i in range(tamanho)]
    return inversa

def matrizB(matriz):
    linhas = len(matriz)
    colunas = len(matriz[0])
    if linhas == colunas:
        return matriz
    elif colunas >= linhas:
        return [linha[:linhas] for linha in matriz]
    else:
        raise ValueError("Não é possível formar submatriz quadrada (mais linhas que colunas).")

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
    matrizB = matrizB(matriz_A)
    print("\nMatriz B:")
    for linha in matrizB:
        print(linha)

    det = determinante_laplace(matrizB)
    print("\nDeterminante (por Laplace):", det)

    if det != 0:
        inversa = matriz_inversa(matrizB)
        print("\nMatriz Inversa:")
        for linha in inversa:
            print(["{:.2f}".format(x) for x in linha])
    else:
        print("\nA matriz não possui inversa (determinante = 0).")

except ValueError as e:
    print("Erro ao extrair submatriz quadrada:", e)
