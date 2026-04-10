import pandas as pd
import numpy as np
from itertools import combinations
import random

def carregar_dados_taco(arquivo_csv):
    """Carrega os dados da tabela TACO"""
    try:
        # Tenta diferentes separadores
        for sep in [';', ',', '\t']:
            try:
                df = pd.read_csv(arquivo_csv, sep=sep, encoding='utf-8')
                if len(df.columns) > 1:
                    break
            except:
                continue

        # Limpa colunas vazias
        df = df.dropna(axis=1, how='all')

        # Padroniza nomes das colunas
        colunas_esperadas = ['numero', 'tipo', 'descricao', 'total - g', 'calorias - kcal', 
                           'protei - g', 'gordura - g', 'caarboidrato - g', 'fibra alimentar - g']

        if len(df.columns) >= len(colunas_esperadas):
            df.columns = colunas_esperadas[:len(df.columns)]

        # Remove linhas com dados inválidos
        df = df.dropna(subset=['calorias - kcal', 'protei - g'])

        # Converte colunas numéricas
        colunas_numericas = ['calorias - kcal', 'protei - g', 'gordura - g', 'caarboidrato - g', 'fibra alimentar - g']
        for col in colunas_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        print(f"Dados TACO carregados: {len(df)} alimentos")
        return df

    except Exception as e:
        print(f"Erro ao carregar dados TACO: {e}")
        return None

def carregar_proporcoes(arquivo_proporcoes):
    """Carrega as proporções por tipo de paciente"""
    try:
        df_prop = pd.read_csv(arquivo_proporcoes)
        proporcoes = {}

        for _, row in df_prop.iterrows():
            tipo = int(row['tipo_paciente'])
            tipo_prop = row['tipo_proporcao']

            if tipo not in proporcoes:
                proporcoes[tipo] = {}

            proporcoes[tipo][tipo_prop] = {
                'cafe_da_manha': float(row['cafe_da_manha']) / 100,
                'lanche_da_manha': float(row['lanche_da_manha']) / 100,
                'almoco': float(row['almoco']) / 100,
                'lanche_da_tarde': float(row['lanche_da_tarde']) / 100,
                'jantar': float(row['jantar']) / 100
            }

        print(f"Proporções carregadas para {len(proporcoes)} tipos de pacientes")
        return proporcoes

    except Exception as e:
        print(f"Erro ao carregar proporções: {e}")
        return None

def carregar_preferencias(arquivo_preferencias, df_taco):
    """Carrega preferências do arquivo de texto"""
    preferencias = {}

    try:
        with open(arquivo_preferencias, 'r', encoding='utf-8') as f:
            linhas = f.readlines()

        for linha in linhas:
            linha = linha.strip()
            if not linha or linha.startswith('#'):
                continue

            partes = linha.split(':')
            if len(partes) != 2:
                continue

            chave = partes[0].strip()
            valores = [v.strip() for v in partes[1].split(',')]

            # Expande valores que são tipos de alimentos
            valores_expandidos = []
            for valor in valores:
                if valor.isdigit():
                    valores_expandidos.append(int(valor))
                else:
                    # É um tipo de alimento
                    alimentos_tipo = df_taco[df_taco['tipo'].str.contains(valor, case=False, na=False)]['numero'].tolist()
                    valores_expandidos.extend(alimentos_tipo)

            preferencias[chave] = valores_expandidos

    except Exception as e:
        print(f"Erro ao carregar preferências: {e}")
        return {}

    return preferencias

def obter_preferencias_dia(preferencias, dia_semana, tipo_refeicao):
    """Obtém preferências para um dia e tipo de refeição específicos"""
    chave_especifica = f"{dia_semana}_{tipo_refeicao}"
    chave_geral = f"todos_{tipo_refeicao}"

    for sufixo in ['_gosta', '_nao_gosta', '_proibido']:
        chave_completa = chave_especifica + sufixo
        chave_geral_completa = chave_geral + sufixo

        if chave_completa in preferencias:
            return preferencias.get(chave_completa, [])
        elif chave_geral_completa in preferencias:
            return preferencias.get(chave_geral_completa, [])

    return []

def gerar_combinacao_refeicao(df_taco, calorias_alvo, proteina_alvo, preferencias_dia, tipo_refeicao, max_tentativas=1000):
    """Gera uma combinação de alimentos para uma refeição com controle rigoroso de calorias (±1%)"""

    # Margem de erro de 1%
    margem_calorias = calorias_alvo * 0.01
    cal_min = calorias_alvo - margem_calorias
    cal_max = calorias_alvo + margem_calorias

    # Obter preferências
    gosta = obter_preferencias_dia(preferencias_dia, 'todos', f"{tipo_refeicao}_gosta")
    nao_gosta = obter_preferencias_dia(preferencias_dia, 'todos', f"{tipo_refeicao}_nao_gosta")
    proibido = obter_preferencias_dia(preferencias_dia, 'todos', f"{tipo_refeicao}_proibido")

    # Filtrar alimentos disponíveis
    alimentos_disponiveis = df_taco.copy()

    # Remove proibidos
    if proibido:
        alimentos_disponiveis = alimentos_disponiveis[~alimentos_disponiveis['numero'].isin(proibido)]

    # Prioriza alimentos que gosta
    if gosta:
        alimentos_preferidos = alimentos_disponiveis[alimentos_disponiveis['numero'].isin(gosta)]
        if len(alimentos_preferidos) > 0:
            alimentos_disponiveis = alimentos_preferidos

    # Remove alimentos que não gosta (se não há preferidos suficientes)
    if nao_gosta and len(alimentos_disponiveis) > 10:
        alimentos_disponiveis = alimentos_disponiveis[~alimentos_disponiveis['numero'].isin(nao_gosta)]

    if len(alimentos_disponiveis) == 0:
        return None, "Nenhum alimento disponível com as restrições"

    melhor_combinacao = None
    melhor_diferenca = float('inf')

    # Tenta diferentes combinações
    for tentativa in range(max_tentativas):
        # Número de alimentos na combinação (1 a 4)
        num_alimentos = random.randint(1, min(4, len(alimentos_disponiveis)))

        # Seleciona alimentos aleatórios
        alimentos_selecionados = alimentos_disponiveis.sample(n=num_alimentos)

        # Tenta diferentes quantidades
        combinacao = []
        calorias_total = 0
        proteina_total = 0

        for _, alimento in alimentos_selecionados.iterrows():
            # Quantidade entre 30g e 200g
            quantidade = random.randint(30, 200)
            fator = quantidade / 100

            cal_alimento = alimento['calorias - kcal'] * fator
            prot_alimento = alimento['protei - g'] * fator

            combinacao.append({
                'numero': alimento['numero'],
                'descricao': alimento['descricao'],
                'quantidade': quantidade,
                'calorias': cal_alimento,
                'proteina': prot_alimento,
                'gordura': alimento['gordura - g'] * fator,
                'carboidrato': alimento['caarboidrato - g'] * fator,
                'fibra': alimento['fibra alimentar - g'] * fator
            })

            calorias_total += cal_alimento
            proteina_total += prot_alimento

        # Verifica se está dentro da margem de 1%
        if cal_min <= calorias_total <= cal_max:
            diferenca_cal = abs(calorias_total - calorias_alvo)
            diferenca_prot = abs(proteina_total - proteina_alvo)
            diferenca_total = diferenca_cal + diferenca_prot

            if diferenca_total < melhor_diferenca:
                melhor_diferenca = diferenca_total
                melhor_combinacao = combinacao

                # Se está muito próximo, aceita
                if diferenca_cal < calorias_alvo * 0.005:  # 0.5%
                    break

    return melhor_combinacao, None

def gerar_dieta_personalizada():
    """Função principal para gerar dieta personalizada"""
    print("=== SISTEMA DE GERAÇÃO DE DIETA PERSONALIZADA ===\n")

    # Carrega dados TACO
    df_taco = carregar_dados_taco('TACO_Base_Paula.csv')
    if df_taco is None:
        return

    # Carrega proporções
    proporcoes = carregar_proporcoes('proporcoes_pacientes.csv')
    if proporcoes is None:
        return

    # Mostra tipos de pacientes disponíveis
    print("Tipos de pacientes disponíveis:")
    for tipo in sorted(proporcoes.keys()):
        print(f"  Tipo {tipo}")

    # Solicita dados do paciente
    try:
        tipo_paciente = int(input("\nDigite o tipo de paciente: "))
        if tipo_paciente not in proporcoes:
            print(f"Tipo de paciente {tipo_paciente} não encontrado!")
            return

        calorias_diarias = float(input("Calorias diárias necessárias: "))
        proteina_minima_diaria = float(input("Proteína mínima diária (g): "))
        arquivo_preferencias = input("Arquivo de preferências (ex: preferencias.txt): ")

    except ValueError:
        print("Erro: Digite valores numéricos válidos")
        return

    # Carrega preferências
    preferencias = carregar_preferencias(arquivo_preferencias, df_taco)

    # Obtém proporções para o tipo de paciente
    prop_calorias = proporcoes[tipo_paciente]['calorias']
    prop_proteina = proporcoes[tipo_paciente]['proteina']

    # Calcula distribuição por refeição
    calorias_refeicoes = {}
    proteina_refeicoes = {}

    for refeicao in ['cafe_da_manha', 'lanche_da_manha', 'almoco', 'lanche_da_tarde', 'jantar']:
        calorias_refeicoes[refeicao] = calorias_diarias * prop_calorias[refeicao]
        proteina_refeicoes[refeicao] = proteina_minima_diaria * prop_proteina[refeicao]

    print(f"\n=== DIETA PARA PACIENTE TIPO {tipo_paciente} ===")
    print(f"Calorias diárias: {calorias_diarias:.0f} kcal")
    print(f"Proteína mínima: {proteina_minima_diaria:.1f}g")
    print("\n" + "="*80)

    dieta_completa = {}
    calorias_total_dia = 0
    proteina_total_dia = 0

    nomes_refeicoes = {
        'cafe_da_manha': 'CAFÉ DA MANHÃ',
        'lanche_da_manha': 'LANCHE DA MANHÃ', 
        'almoco': 'ALMOÇO',
        'lanche_da_tarde': 'LANCHE DA TARDE',
        'jantar': 'JANTAR'
    }

    # Gera cada refeição
    for refeicao in ['cafe_da_manha', 'lanche_da_manha', 'almoco', 'lanche_da_tarde', 'jantar']:
        print(f"\n{nomes_refeicoes[refeicao]}")
        print(f"Meta: {calorias_refeicoes[refeicao]:.0f} kcal | {proteina_refeicoes[refeicao]:.1f}g proteína")
        print("-" * 60)

        combinacao, erro = gerar_combinacao_refeicao(
            df_taco, 
            calorias_refeicoes[refeicao], 
            proteina_refeicoes[refeicao],
            preferencias, 
            refeicao
        )

        if combinacao:
            dieta_completa[refeicao] = combinacao
            cal_refeicao = sum(item['calorias'] for item in combinacao)
            prot_refeicao = sum(item['proteina'] for item in combinacao)

            for item in combinacao:
                print(f"• {item['descricao']} - {item['quantidade']}g")
                print(f"  {item['calorias']:.1f} kcal | {item['proteina']:.1f}g prot | "
                      f"{item['gordura']:.1f}g gord | {item['carboidrato']:.1f}g carb")

            print(f"\nTOTAL DA REFEIÇÃO: {cal_refeicao:.1f} kcal | {prot_refeicao:.1f}g proteína")

            # Verifica se está dentro da margem de 1%
            margem = calorias_refeicoes[refeicao] * 0.01
            if abs(cal_refeicao - calorias_refeicoes[refeicao]) <= margem:
                print("✓ Dentro da margem de 1%")
            else:
                print("⚠ Fora da margem de 1%")

            calorias_total_dia += cal_refeicao
            proteina_total_dia += prot_refeicao
        else:
            print(f"❌ Erro ao gerar refeição: {erro}")

    # Resumo final
    print("\n" + "="*80)
    print("RESUMO NUTRICIONAL DO DIA")
    print("="*80)
    print(f"Calorias totais: {calorias_total_dia:.1f} kcal (Meta: {calorias_diarias:.0f} kcal)")
    print(f"Proteína total: {proteina_total_dia:.1f}g (Meta: {proteina_minima_diaria:.1f}g)")

    # Verifica margem total
    margem_total = calorias_diarias * 0.01
    if abs(calorias_total_dia - calorias_diarias) <= margem_total:
        print("✓ DIETA DENTRO DA MARGEM DE 1%")
    else:
        print("⚠ DIETA FORA DA MARGEM DE 1%")

    return dieta_completa

if __name__ == "__main__":
    gerar_dieta_personalizada()
