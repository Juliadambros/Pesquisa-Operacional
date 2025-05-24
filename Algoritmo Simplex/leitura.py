import re

def extrair_termos(expr):
    expr = expr.replace(" ", "").replace(",", ".")
    if re.search(r'[a-wy-zA-WY-Z]', expr):
        raise ValueError("Expressão contém variáveis inválidas. Use apenas 'x' seguido de número.")

    matches = re.findall(r'([+-]?\d*\.?\d*)(x\d+)', expr)
    termos = []
    for coef_str, var_str in matches:
        coef = float(coef_str) if coef_str not in ['', '+', '-'] else (1.0 if coef_str != '-' else -1.0)
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

    matriz_A, vetor_b, tipos_restricao, variaveis_folga = [], [], [], 0
    for linha in linhas[1:]:
        linha = linha.strip()
        if not linha:
            continue

        if ">=" in linha: operador, coefE, coefD = ">=", *linha.split(">=")
        elif "<=" in linha: operador, coefE, coefD = "<=", *linha.split("<=")
        elif "=" in linha: operador, coefE, coefD = "=", *linha.split("=")
        else: continue

        partes = extrair_termos(coefE.strip())
        resultado = float(coefD.strip().replace(',', '.'))

        equacao = [0] * (quantidade_variaveis + variaveis_folga)
        for coef, var in partes:
            equacao[var - 1] = coef

        equacao.append(-1 if operador == ">=" else (1 if operador == "<=" else 0))
        matriz_A.append(equacao)
        vetor_b.append(resultado)
        tipos_restricao.append(operador)
        variaveis_folga += 1

    for linha in matriz_A:
        while len(linha) < quantidade_variaveis + variaveis_folga:
            linha.append(0)
    vetor_c.extend([0] * (len(matriz_A[0]) - len(vetor_c)))

    return matriz_A, vetor_b, vetor_c, tipo_otimizacao, tipos_restricao

