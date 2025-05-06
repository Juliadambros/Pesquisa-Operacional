import re

def extrair_termos(expr):
    expr = expr.replace(" ", "").replace(",", ".")

    # Verifica se existem variáveis inválidas (excluindo 'x')
    if re.search(r'[a-wy-zA-WY-Z]', expr):  # ignora 'x', mas bloqueia outras letras
        raise ValueError("Expressão contém variáveis inválidas. Use apenas 'x' seguido de número.")

    # Encontra os coeficientes e as variáveis da expressão
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

