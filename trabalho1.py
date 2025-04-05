import re

def extrair_termos(expr):
    expr = expr.replace(" ", "")
    matches = re.findall(r'([+-]?[\d]*)(x\d+)', expr)
    termos = []
    for coef_str, var_str in matches:
        if coef_str in ['', '+']:
            coef = 1
        elif coef_str == '-':
            coef = -1
        else:
            coef = int(coef_str)
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
    matriz_original = []
    vetor_b = []
    variaveis_folga = 0

    for linha in linhas[1:]:
        linha = linha.strip()
        if not linha:
            continue

        if ">=" in linha:
            operador = ">="
            lhs, rhs = linha.split(">=")
        elif "<=" in linha:
            operador = "<="
            lhs, rhs = linha.split("<=")
        elif "=" in linha:
            operador = "="
            lhs, rhs = linha.split("=")
        else:
            continue

        partes = extrair_termos(lhs.strip())
        resultado = int(rhs.strip())

        # Matriz original: apenas variáveis reais + resultado
        linha_original = [0] * quantidade_variaveis
        for coef, var in partes:
            linha_original[var - 1] = coef
        matriz_original.append(linha_original + [resultado])  # Inclui o vetor_b

        # Matriz A com folgas
        equacao = [0] * (quantidade_variaveis + variaveis_folga)
        for coef, var in partes:
            equacao[var - 1] = coef

        if operador == ">=":
            equacao.append(-1)
        elif operador == "<=":
            equacao.append(1)
        else:
            equacao.append(0)

        matriz_A.append(equacao)
        vetor_b.append(resultado)
        variaveis_folga += 1

    for linha in matriz_A:
        while len(linha) < quantidade_variaveis + variaveis_folga:
            linha.append(0)

    vetor_c.extend([0] * (len(matriz_A[0]) - len(vetor_c)))

    return matriz_A, vetor_b, vetor_c, tipo_otimizacao, matriz_original


# Execução principal
arquivo = "exercicio.txt"
matriz_A, vetor_b, vetor_c, tipo_otimizacao, matriz_original = ler_arquivo(arquivo)

print("Matriz A (com folgas):")
for linha in matriz_A:
    print(linha)

print("\nMatriz original:")
for linha in matriz_original:
    print(linha)

print("\nVetor b:")
for coef in vetor_b:
    print(f"[{coef}]")

print("Vetor C:", vetor_c)

print("Tipo de otimização:", tipo_otimizacao)

# Verifica se matriz_original é quadrada (desconsiderando última coluna)? 

