import pandas as pd
import random

def carregar_taco(arquivo_taco):
    """Carrega a tabela TACO a partir de um arquivo CSV."""
    taco = pd.read_csv(arquivo_taco, sep=';')
    taco.columns = taco.columns.str.replace(r'\W', '', regex=True)
    taco = taco.rename(columns={
        'totalg': 'totalg', 
        'proteig': 'proteig', 
        'gordurag': 'gordurag', 
        'caarboidratog': 'caarboidratog', 
        'fibraalimentarg': 'fibraalimentarg'
    })
    return taco

def obter_alimentos_por_tipo(taco, tipo):
    """Retorna lista de números dos alimentos de um tipo específico."""
    alimentos_tipo = taco[taco['tipo'].str.lower() == tipo.lower()]
    return alimentos_tipo['numero'].tolist()

def obter_tipos_disponiveis(taco):
    """Retorna lista de todos os tipos disponíveis na tabela TACO."""
    return sorted(taco['tipo'].str.lower().unique())

def expandir_preferencias(taco, lista_preferencias):
    """Expande uma lista de preferências que pode conter números ou tipos.

    Args:
        taco: DataFrame da tabela TACO
        lista_preferencias: Lista contendo números de alimentos e/ou nomes de tipos

    Returns:
        Lista de números de alimentos expandida
    """
    alimentos_expandidos = []
    tipos_disponiveis = obter_tipos_disponiveis(taco)

    for item in lista_preferencias:
        try:
            # Tenta converter para número (alimento específico)
            numero_alimento = int(item)
            if 1 <= numero_alimento <= len(taco):
                alimentos_expandidos.append(numero_alimento)
            else:
                print(f"Aviso: Alimento {numero_alimento} não existe na tabela TACO")
        except ValueError:
            # Se não é número, trata como tipo de alimento
            tipo_nome = str(item).strip().lower()
            if tipo_nome in tipos_disponiveis:
                alimentos_do_tipo = obter_alimentos_por_tipo(taco, tipo_nome)
                alimentos_expandidos.extend(alimentos_do_tipo)
                print(f"Expandindo tipo '{tipo_nome}': {len(alimentos_do_tipo)} alimentos adicionados")
            else:
                print(f"Aviso: Tipo '{tipo_nome}' não encontrado. Tipos disponíveis: {', '.join(tipos_disponiveis)}")

    # Remove duplicatas e retorna lista ordenada
    return sorted(list(set(alimentos_expandidos)))

def carregar_preferencias(arquivo_preferencias, taco):
    """Carrega as preferências alimentares a partir de um arquivo TXT.
    Sistema por exceção com hierarquia: dia específico > todos > sem restrição.
    Suporta números de alimentos específicos e nomes de tipos."""
    dias = ['seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom', 'todos']
    refeicoes = ['cafe_da_manha', 'lanche_da_manha', 'almoco', 'lanche_da_tarde', 'jantar']
    tipos = ['gosta', 'nao_gosta', 'nao_pode', 'obrigatorio']

    # Inicializa estrutura vazia - padrão é aceitar tudo
    preferencias = {dia: {ref: {tp: [] for tp in tipos} for ref in refeicoes} for dia in dias}

    print(f"\nTipos de alimentos disponíveis: {', '.join(obter_tipos_disponiveis(taco))}")
    print("Você pode usar números específicos (ex: 1,2,3) ou nomes de tipos (ex: cereais,carnes)")

    try:
        with open(arquivo_preferencias, 'r', encoding='utf-8') as arquivo:
            for linha_num, linha in enumerate(arquivo, 1):
                linha = linha.strip()
                if linha and not linha.startswith('#'):  # Ignora linhas vazias e comentários
                    partes = linha.split(',')
                    if len(partes) >= 3:  # Mínimo: dia, refeicao, tipo
                        dia = partes[0].strip().lower()
                        refeicao = partes[1].strip().lower()
                        tipo = partes[2].strip().lower()

                        # Se há alimentos/tipos especificados
                        if len(partes) > 3:
                            items_brutos = [x.strip() for x in partes[3:] if x.strip()]
                            # Expande números e tipos para lista de números de alimentos
                            alimentos = expandir_preferencias(taco, items_brutos)
                        else:
                            alimentos = []

                        # Verifica se dia, refeição e tipo são válidos
                        if dia in preferencias and refeicao in preferencias[dia] and tipo in preferencias[dia][refeicao]:
                            preferencias[dia][refeicao][tipo] = alimentos
                            if alimentos:
                                print(f"Linha {linha_num}: {dia}/{refeicao}/{tipo} = {len(alimentos)} alimentos")
                        else:
                            print(f"Aviso: Linha {linha_num} ignorada (dia/refeição/tipo inválido): {linha}")
                    else:
                        print(f"Aviso: Linha {linha_num} com formato inválido: {linha}")

    except FileNotFoundError:
        print("Arquivo de preferências não encontrado. Usando sistema padrão (aceita tudo).")
    except Exception as e:
        print(f"Erro ao carregar preferências: {e}. Usando sistema padrão (aceita tudo).")

    return preferencias

def obter_preferencias_dia(preferencias, dia, refeicao):
    """Obtém as preferências para um dia/refeição específico seguindo a hierarquia:
    1. Dia específico
    2. 'todos' (se dia específico não existir)
    3. Sem restrição (se nem dia nem 'todos' existirem)"""

    dias_semana = ['seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom']
    tipos = ['gosta', 'nao_gosta', 'nao_pode', 'obrigatorio']

    # Inicializa preferências vazias (sem restrição)
    pref_resultado = {tp: [] for tp in tipos}

    # Verifica se existe configuração para o dia específico
    tem_config_dia = any(
        preferencias[dia][refeicao][tipo] 
        for tipo in tipos 
        if preferencias[dia][refeicao][tipo]
    )

    if tem_config_dia:
        # Usa as preferências do dia específico
        pref_resultado = preferencias[dia][refeicao].copy()
        fonte = f"dia específico ({dia})"
    else:
        # Verifica se existe configuração para 'todos'
        tem_config_todos = any(
            preferencias['todos'][refeicao][tipo] 
            for tipo in tipos 
            if preferencias['todos'][refeicao][tipo]
        )

        if tem_config_todos:
            # Usa as preferências de 'todos'
            pref_resultado = preferencias['todos'][refeicao].copy()
            fonte = "'todos'"
        else:
            # Usa sem restrição (já inicializado vazio)
            fonte = "sem restrição"

    return pref_resultado, fonte

def obter_alimentos_ricos_proteina(taco, top_n=20):
    """Retorna os alimentos com maior teor de proteína por 100g."""
    # Ordena por proteína em ordem decrescente
    taco_ordenado = taco.sort_values('proteig', ascending=False)
    # Retorna os IDs dos top alimentos (índice + 1)
    return (taco_ordenado.head(top_n).index + 1).tolist()

def gerar_refeicao(taco, preferencias_refeicao, calorias_refeicao, proteina_necessaria=0, priorizar_proteina=False):
    """Gera uma refeição com base nas preferências, restrições e necessidade de proteína."""
    obrigatorios = preferencias_refeicao.get('obrigatorio', [])
    nao_pode = set(preferencias_refeicao.get('nao_pode', []))
    gosta = preferencias_refeicao.get('gosta', [])

    # Todos os alimentos disponíveis (1 até o número total de alimentos)
    todos_alimentos = list(range(1, len(taco) + 1))

    # Remove apenas os que não pode comer
    alimentos_permitidos = [i for i in todos_alimentos if i not in nao_pode]

    # Remove obrigatórios da lista de permitidos para não duplicar
    alimentos_para_completar = [i for i in alimentos_permitidos if i not in obrigatorios]

    # Se precisa priorizar proteína, obtém alimentos ricos em proteína
    if priorizar_proteina:
        alimentos_ricos_proteina = obter_alimentos_ricos_proteina(taco)
        alimentos_proteina_permitidos = [i for i in alimentos_ricos_proteina if i in alimentos_para_completar]

        if alimentos_proteina_permitidos:
            # Prioriza alimentos ricos em proteína
            alimentos_usaveis = alimentos_proteina_permitidos
        else:
            # Se não há alimentos ricos em proteína permitidos, usa todos
            alimentos_usaveis = alimentos_para_completar
    else:
        # Se há preferências de "gosta", prioriza esses alimentos
        if gosta:
            alimentos_preferidos = [i for i in alimentos_para_completar if i in gosta]
            if alimentos_preferidos:
                alimentos_usaveis = alimentos_preferidos
            else:
                alimentos_usaveis = alimentos_para_completar
        else:
            # Se não há preferências específicas, usa todos os permitidos
            alimentos_usaveis = alimentos_para_completar

    refeicao = []
    calorias_acumuladas = 0
    proteinas_acumuladas = 0
    gorduras_acumuladas = 0
    carboidratos_acumulados = 0

    # Primeiro, inclui alimentos obrigatórios
    for alimento_id in obrigatorios:
        if alimento_id <= len(taco):
            alimento = taco.iloc[alimento_id - 1]
            if alimento['caloriaskcal'] > 0:  # Evita divisão por zero
                proporcao = min(100, max(10, (calorias_refeicao - calorias_acumuladas) / alimento['caloriaskcal'] * 100))
            else:
                proporcao = 50  # Valor padrão para alimentos sem calorias

            refeicao.append({
                'descricao': alimento['descricao'],
                'proporcao': proporcao,
                'obrigatorio': True,
                'tipo': alimento['tipo']
            })

            calorias_acumuladas += (alimento['caloriaskcal'] / 100) * proporcao
            proteinas_acumuladas += (alimento['proteig'] / 100) * proporcao
            gorduras_acumuladas += (alimento['gordurag'] / 100) * proporcao
            carboidratos_acumulados += (alimento['caarboidratog'] / 100) * proporcao

    # Depois, completa com outros alimentos
    tentativas = 0
    max_tentativas = 50  # Evita loop infinito

    while (calorias_acumuladas < calorias_refeicao * 0.9 or proteinas_acumuladas < proteina_necessaria) and alimentos_usaveis and tentativas < max_tentativas:
        alimento_id = random.choice(alimentos_usaveis)
        alimento = taco.iloc[alimento_id - 1]

        # Se ainda precisa de proteína, ajusta a proporção para priorizar proteína
        if proteinas_acumuladas < proteina_necessaria and alimento['proteig'] > 0:
            proteina_restante = proteina_necessaria - proteinas_acumuladas
            proporcao_por_proteina = (proteina_restante / alimento['proteig']) * 100
            proporcao_por_caloria = (calorias_refeicao - calorias_acumuladas) / alimento['caloriaskcal'] * 100 if alimento['caloriaskcal'] > 0 else 50
            proporcao = min(100, max(10, max(proporcao_por_proteina, proporcao_por_caloria)))
        else:
            if alimento['caloriaskcal'] > 0:
                calorias_restantes = calorias_refeicao - calorias_acumuladas
                proporcao = min(100, max(10, calorias_restantes / alimento['caloriaskcal'] * 100))
            else:
                proporcao = 30  # Valor padrão para alimentos sem calorias

        refeicao.append({
            'descricao': alimento['descricao'],
            'proporcao': proporcao,
            'obrigatorio': False,
            'tipo': alimento['tipo']
        })

        calorias_acumuladas += (alimento['caloriaskcal'] / 100) * proporcao
        proteinas_acumuladas += (alimento['proteig'] / 100) * proporcao
        gorduras_acumuladas += (alimento['gordurag'] / 100) * proporcao
        carboidratos_acumulados += (alimento['caarboidratog'] / 100) * proporcao

        # Remove o alimento usado para não repeti-lo
        alimentos_usaveis.remove(alimento_id)
        tentativas += 1

    return refeicao, calorias_acumuladas, proteinas_acumuladas, gorduras_acumuladas, carboidratos_acumulados

def gerar_plano_dieta(taco, preferencias, calorias_semana, proteina_minima_diaria):
    """Gera um plano de dieta completo para a semana com controle de proteína mínima."""
    dias = ['seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom']
    refeicoes = ['cafe_da_manha', 'lanche_da_manha', 'almoco', 'lanche_da_tarde', 'jantar']

    plano_semana = {}
    totais_semana = {}
    fontes_preferencias = {}  # Para rastrear de onde vieram as preferências

    for dia in dias:
        print(f"\nProcessando {dia.upper()}...")
        calorias_diarias = calorias_semana[dia]

        # Distribuição calórica por refeição
        calorias_refeicoes = {
            'cafe_da_manha': calorias_diarias * 0.20,
            'lanche_da_manha': calorias_diarias * 0.05,
            'almoco': calorias_diarias * 0.35,
            'lanche_da_tarde': calorias_diarias * 0.10,
            'jantar': calorias_diarias * 0.30
        }

        # Distribuição de proteína por refeição (prioriza almoço e jantar)
        proteina_refeicoes = {
            'cafe_da_manha': proteina_minima_diaria * 0.15,
            'lanche_da_manha': proteina_minima_diaria * 0.05,
            'almoco': proteina_minima_diaria * 0.40,
            'lanche_da_tarde': proteina_minima_diaria * 0.10,
            'jantar': proteina_minima_diaria * 0.30
        }

        plano_dia = {}
        total_calorias = total_proteinas = total_gorduras = total_carboidratos = 0
        fontes_dia = {}

        # Primeira passada: gera refeições normalmente
        for refeicao in refeicoes:
            # Obtém as preferências seguindo a hierarquia
            pref_refeicao, fonte = obter_preferencias_dia(preferencias, dia, refeicao)
            fontes_dia[refeicao] = fonte

            alimentos, calorias, proteinas, gorduras, carboidratos = gerar_refeicao(
                taco, pref_refeicao, calorias_refeicoes[refeicao], proteina_refeicoes[refeicao]
            )

            plano_dia[refeicao] = alimentos
            total_calorias += calorias
            total_proteinas += proteinas
            total_gorduras += gorduras
            total_carboidratos += carboidratos

        # Verifica se atingiu a proteína mínima
        if total_proteinas < proteina_minima_diaria:
            print(f"  Proteína insuficiente ({total_proteinas:.1f}g < {proteina_minima_diaria}g). Ajustando...")

            # Refeições que podem ser ajustadas (almoço e jantar têm prioridade)
            refeicoes_ajuste = ['almoco', 'jantar', 'cafe_da_manha']

            for refeicao_ajuste in refeicoes_ajuste:
                if total_proteinas >= proteina_minima_diaria:
                    break

                proteina_faltante = proteina_minima_diaria - total_proteinas
                pref_refeicao, _ = obter_preferencias_dia(preferencias, dia, refeicao_ajuste)

                # Regenera a refeição priorizando proteína
                alimentos_novos, cal_nova, prot_nova, gord_nova, carb_nova = gerar_refeicao(
                    taco, pref_refeicao, calorias_refeicoes[refeicao_ajuste], 
                    proteina_refeicoes[refeicao_ajuste] + proteina_faltante, 
                    priorizar_proteina=True
                )

                # Atualiza os totais (remove valores antigos da refeição)
                for alimento in plano_dia[refeicao_ajuste]:
                    # Busca o alimento na tabela TACO pela descrição
                    alimento_taco = taco[taco['descricao'] == alimento['descricao']]
                    if not alimento_taco.empty:
                        proporcao = alimento['proporcao']
                        total_calorias -= (alimento_taco.iloc[0]['caloriaskcal'] / 100) * proporcao
                        total_proteinas -= (alimento_taco.iloc[0]['proteig'] / 100) * proporcao
                        total_gorduras -= (alimento_taco.iloc[0]['gordurag'] / 100) * proporcao
                        total_carboidratos -= (alimento_taco.iloc[0]['caarboidratog'] / 100) * proporcao

                plano_dia[refeicao_ajuste] = alimentos_novos
                total_calorias += cal_nova
                total_proteinas += prot_nova
                total_gorduras += gord_nova
                total_carboidratos += carb_nova

        plano_semana[dia] = plano_dia
        totais_semana[dia] = {
            'calorias': total_calorias,
            'proteinas': total_proteinas,
            'gorduras': total_gorduras,
            'carboidratos': total_carboidratos,
            'proteina_minima': proteina_minima_diaria,
            'proteina_atingida': total_proteinas >= proteina_minima_diaria
        }
        fontes_preferencias[dia] = fontes_dia

    return plano_semana, totais_semana, fontes_preferencias

def imprimir_plano_semana(plano_semana, totais_semana, fontes_preferencias):
    """Imprime o plano de dieta semanal de forma organizada."""
    dias = ['seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom']

    print("\n" + "="*80)
    print("PLANO DE DIETA SEMANAL PERSONALIZADO")
    print("="*80)

    for dia in dias:
        print(f"\n{'='*20} {dia.upper()} {'='*20}")

        for refeicao, alimentos in plano_semana[dia].items():
            fonte = fontes_preferencias[dia][refeicao]
            print(f"\n{refeicao.replace('_', ' ').title()} (baseado em: {fonte}):")

            if alimentos:
                for alimento in alimentos:
                    marcador = "★" if alimento.get('obrigatorio', False) else "•"
                    tipo_info = f"[{alimento.get('tipo', 'N/A')}]"
                    print(f"  {marcador} {alimento['descricao']} ({alimento['proporcao']:.1f}g) {tipo_info}")
            else:
                print("  • Sem opções disponíveis com as restrições informadas.")

        # Status da proteína
        proteina_status = "✓" if totais_semana[dia]['proteina_atingida'] else "⚠"

        print(f"\nTotais do dia:")
        print(f"  Calorias: {totais_semana[dia]['calorias']:.1f} kcal")
        print(f"  Proteínas: {totais_semana[dia]['proteinas']:.1f}g {proteina_status} (mín: {totais_semana[dia]['proteina_minima']:.1f}g)")
        print(f"  Gorduras: {totais_semana[dia]['gorduras']:.1f} g")
        print(f"  Carboidratos: {totais_semana[dia]['carboidratos']:.1f} g")

def salvar_plano_arquivo(plano_semana, totais_semana, fontes_preferencias, nome_arquivo="plano_dieta_semanal.txt"):
    """Salva o plano de dieta em um arquivo de texto."""
    dias = ['seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom']

    with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
        arquivo.write("PLANO DE DIETA SEMANAL PERSONALIZADO\n")
        arquivo.write("="*80 + "\n")

        for dia in dias:
            arquivo.write(f"\n{'='*20} {dia.upper()} {'='*20}\n")

            for refeicao, alimentos in plano_semana[dia].items():
                fonte = fontes_preferencias[dia][refeicao]
                arquivo.write(f"\n{refeicao.replace('_', ' ').title()} (baseado em: {fonte}):\n")

                if alimentos:
                    for alimento in alimentos:
                        marcador = "★" if alimento.get('obrigatorio', False) else "•"
                        tipo_info = f"[{alimento.get('tipo', 'N/A')}]"
                        arquivo.write(f"  {marcador} {alimento['descricao']} ({alimento['proporcao']:.1f}g) {tipo_info}\n")
                else:
                    arquivo.write("  • Sem opções disponíveis com as restrições informadas.\n")

            proteina_status = "✓" if totais_semana[dia]['proteina_atingida'] else "⚠"

            arquivo.write(f"\nTotais do dia:\n")
            arquivo.write(f"  Calorias: {totais_semana[dia]['calorias']:.1f} kcal\n")
            arquivo.write(f"  Proteínas: {totais_semana[dia]['proteinas']:.1f}g {proteina_status} (mín: {totais_semana[dia]['proteina_minima']:.1f}g)\n")
            arquivo.write(f"  Gorduras: {totais_semana[dia]['gorduras']:.1f} g\n")
            arquivo.write(f"  Carboidratos: {totais_semana[dia]['carboidratos']:.1f} g\n")

    print(f"\nPlano de dieta salvo em: {nome_arquivo}")

def main():
    """Função principal do sistema."""
    print("Sistema de Geração de Dieta Personalizada - TACO")
    print("="*50)
    print("Hierarquia de preferências:")
    print("1. Dia específico (seg, ter, qua, qui, sex, sab, dom)")
    print("2. 'todos' (se dia específico não existir)")
    print("3. Sem restrição (se nem dia nem 'todos' existirem)")
    print("\nSuporta números específicos (ex: 1,2,3) e tipos (ex: cereais,carnes)")
    print("="*50)

    # Carregar dados
    arquivo_taco = 'TACO_Base_Paula.csv'
    arquivo_preferencias = 'preferencias.txt'

    print("\nCarregando tabela TACO...")
    taco = carregar_taco(arquivo_taco)
    print(f"Tabela TACO carregada: {len(taco)} alimentos disponíveis")

    print("\nCarregando preferências...")
    preferencias = carregar_preferencias(arquivo_preferencias, taco)
    print("Preferências carregadas com hierarquia: dia específico > 'todos' > sem restrição")

    # Obter proteína mínima diária
    while True:
        try:
            proteina_minima = float(input("\nDigite a quantidade mínima de proteína diária (g): "))
            if proteina_minima > 0:
                break
            else:
                print("Por favor, digite um valor positivo.")
        except ValueError:
            print("Por favor, digite um número válido.")

    # Obter calorias para cada dia da semana
    print("\nInforme a necessidade calórica para cada dia da semana:")
    dias = ['seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom']
    calorias_semana = {}

    for dia in dias:
        while True:
            try:
                calorias = float(input(f"Calorias para {dia}: "))
                if calorias > 0:
                    calorias_semana[dia] = calorias
                    break
                else:
                    print("Por favor, digite um valor positivo.")
            except ValueError:
                print("Por favor, digite um número válido.")

    # Gerar plano semanal
    print("\nGerando plano de dieta semanal...")
    plano_semana, totais_semana, fontes_preferencias = gerar_plano_dieta(taco, preferencias, calorias_semana, proteina_minima)

    # Imprimir resultado
    imprimir_plano_semana(plano_semana, totais_semana, fontes_preferencias)

    # Salvar em arquivo
    salvar_plano_arquivo(plano_semana, totais_semana, fontes_preferencias)

    print("\n" + "="*80)
    print("LEGENDA:")
    print("★ = Alimento obrigatório")
    print("• = Alimento sugerido")
    print("✓ = Proteína mínima atingida")
    print("⚠ = Proteína mínima NÃO atingida")
    print("[tipo] = Categoria do alimento")
    print("\nHIERARQUIA DE PREFERÊNCIAS:")
    print("1. Dia específico → 2. 'todos' → 3. Sem restrição")
    print("\nFORMATO DE PREFERÊNCIAS:")
    print("- Números específicos: 1,2,3,4")
    print("- Tipos de alimentos: cereais,carnes,frutas")
    print("- Misturado: 1,2,cereais,carnes")
    print("="*80)

if __name__ == "__main__":
    main()
