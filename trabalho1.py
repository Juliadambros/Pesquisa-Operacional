def ler_arquivo(arquivo):
    with open(arquivo, 'r') as arquivo:
        linhas = arquivo.readlines()  
    
    primeira_linha = linhas[0].lower()  
    # lower serve para que não tenha problema em letras Maiúsculas ou Minúsculas
    tipo_otimizacao = "max" if "max" in primeira_linha else "min"
    
    funcao = primeira_linha.split('=')[1].strip() # split separa a primeira linha para o vetor C (valores depois do =), strip tira os espaços vazios
    termos = [] #onde os coeficientes e variaveis são guardados para o vetor C
    i = 0
    while i < len(funcao):
        if funcao[i] == 'x':  
            coeficiente = 1
            j = i - 1
            # Procurando pelo coeficiente
            while j >= 0 and (funcao[j] == '+' or funcao[j] == '-' or funcao[j].isdigit()):
                j -= 1
            if j+1 < i:  #algo entre x e o coeficiente
                valor_coef = funcao[j+1:i]
                # Verificar se valor_coef é um número válido antes de convertê-lo
                if valor_coef and valor_coef not in ['+', '-']:
                    coeficiente = int(valor_coef)
                elif valor_coef == '-':
                    coeficiente = -1
                elif valor_coef == '+':
                    coeficiente = 1
            #if funcao[j + 1:i] == '-' and coeficiente == 1:  # Se for 'x' sem coeficiente, assume -1
            #    coeficiente = -1

            termos.append((coeficiente, int(funcao[i+1])))
            i += 2  #próximo termo
        else:
            i += 1
    
    quantidade_variaveis = max(termo[1] for termo in termos)
    vetor_c = [0] * quantidade_variaveis
    
    for coeficiente, variavel in termos:
        vetor_c[variavel - 1] = coeficiente
    print(termos)
    matriz_A = []
    vetor_b = []
    variaveis_folga = 0
    
    for linha in linhas[1:]:
        linha = linha.strip()
        if not linha:  #ignora linhas vazias
            continue
        
        partes = [] #onde os coeficientes e variaveis são guardados para a matriz A
        i = 0
        while i < len(linha):
            if linha[i] == 'x': 
                coeficiente = 1
                j = i - 1
                while j >= 0 and (linha[j] == '+' or linha[j] == '-' or linha[j].isdigit()):
                    j -= 1
                if j+1 < i: 
                    valor_coef = linha[j+1:i]
                    if valor_coef and valor_coef not in ['+', '-']:
                        coeficiente = int(valor_coef)
                    elif valor_coef == '-':
                        coeficiente = -1
                    elif valor_coef == '+':
                        coeficiente = 1
                partes.append((coeficiente, int(linha[i+1])))
                i += 2  
            else:
                i += 1
        
        operador = ''
        if '>=' in linha:
            operador = '>='
        elif '<=' in linha:
            operador = '<='
        elif '=' in linha:
            operador = '='
        
        resultado = 0  #para o vetor b
        for j in range(len(linha) - 1, -1, -1): #equação de traz para frente
            if linha[j].isdigit() or linha[j] == '+' or linha[j] == '-':
                resultado = int(linha[j:])
                break
        
        equacao = [0] * (quantidade_variaveis + variaveis_folga)
        for coeficiente, variavel in partes:
            equacao[variavel - 1] = coeficiente
        
        if operador == '>=':
            equacao.append(-1)  
        elif operador == '<=':
            equacao.append(1)   
        else:
            equacao.append(0) 
        
        matriz_A.append(equacao)
        variaveis_folga += 1
        vetor_b.append(resultado)
    
    # arrumar a matriz A e vetor C com variáveis de folga
    for linha in matriz_A:
        while len(linha) < quantidade_variaveis + variaveis_folga:
            linha.append(0)
    
    vetor_c.extend([0] * (len(matriz_A[0]) - len(vetor_c)))
    
    return matriz_A, vetor_b, vetor_c, tipo_otimizacao

arquivo = "exercicio.txt"
matriz_A, vetor_b, vetor_c, tipo_otimizacao = ler_arquivo(arquivo)
print("Matriz A:")
for linha in matriz_A:
    print(linha)
print("Vetor b:", vetor_b)
print("Vetor C:", vetor_c)
print("Tipo de otimização:", tipo_otimizacao)
