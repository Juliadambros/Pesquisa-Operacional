import re

def extrair_termos(expr):
    expr = expr.replace(" ", "").replace(",", ".").replace("−", "-")  # substitui menos unicode por traço normal

    if re.search(r'[^0-9xX+\-.,]', expr):
        raise ValueError("Expressão contém caracteres inválidos. Use apenas números, '+', '-', variáveis como x1, x2, etc.")

    if re.search(r'[a-wy-zA-WY-Z]', expr):
        raise ValueError("Expressão contém variáveis inválidas. Use apenas 'x' seguido de número.")

    matches = re.findall(r'([+-]?(?:\d+(?:\.\d+)?|\d*))(x\d+)', expr)
    termos = []
    for coef_str, var_str in matches:
        coef = float(coef_str) if coef_str not in ['', '+', '-'] else (1.0 if coef_str != '-' else -1.0)
        var = int(var_str[1:])
        termos.append((coef, var))
    return termos


def ler_arquivo(caminho_arquivo):
    with open(caminho_arquivo, 'r') as arquivo:
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
    tipos_restricao = []
    variaveis_folga = 0
    indice_folga = 0

    for linha in linhas[1:]:
        linha = linha.strip()
        if not linha:
            continue

        if ">=" in linha:
            operador, coefE, coefD = ">=", *linha.split(">=")
        elif "<=" in linha:
            operador, coefE, coefD = "<=", *linha.split("<=")
        elif ">" in linha:
            operador, coefE, coefD = ">", *linha.split(">")
        elif "<" in linha:
            operador, coefE, coefD = "<", *linha.split("<")
        elif "=" in linha:
            operador, coefE, coefD = "=", *linha.split("=")
        else:
            continue  # Ignorar linhas inválidas

        partes = extrair_termos(coefE.strip())
        resultado = float(coefD.strip().replace(',', '.'))

        if resultado < 0 and operador in ("<=", "<"):
            print(f"ATENÇÃO: restrição '{linha}' tem b < 0 com operador '{operador}'.")
            print("→ Isso pode tornar o problema infactível com variáveis não-negativas (x >= 0).")


        if resultado < 0:
            resultado *= -1
            if operador == ">=":
                operador = "<="
            elif operador == "<=":
                operador = ">="
            elif operador == ">":
                operador = "<"
            elif operador == "<":
                operador = ">"
            partes = [(-coef, var) for coef, var in partes]

        # Inicializar equação com variáveis principais
        equacao = [0] * quantidade_variaveis
        for coef, var in partes:
            equacao[var - 1] = coef

        # Adicionar variáveis de folga 
        if operador in (">=", "<=", ">", "<"):
            equacao += [0] * variaveis_folga
            equacao.append(-1 if operador in (">=", ">") else 1)
            variaveis_folga += 1
            indice_folga += 1
        else:  # operador ==
            equacao += [0] * variaveis_folga
            equacao.append(0)  # Nenhuma variável de folga

        matriz_A.append(equacao)
        vetor_b.append(resultado)
        tipos_restricao.append(operador)

    # Garantir que todas as equações tenham o mesmo tamanho
    tamanho_total = quantidade_variaveis + variaveis_folga
    for linha in matriz_A:
        while len(linha) < tamanho_total:
            linha.append(0)

    # Ajustar vetor c para o mesmo tamanho da matriz A
    vetor_c.extend([0] * (tamanho_total - len(vetor_c)))

    return matriz_A, vetor_b, vetor_c, tipo_otimizacao, tipos_restricao
