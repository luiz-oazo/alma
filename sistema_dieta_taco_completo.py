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

def carregar_preferencias(arquivo_preferencias):
    """Carrega as preferências alimentares a partir de um arquivo TXT.
    Sistema por exceção: se não há informação, aceita tudo."""
    dias = ['seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom']
    refeicoes = ['cafe_da_manha', 'lanche_da_manha', 'almoco', 'lanche_da_tarde', 'jantar']
    tipos = ['gosta', 'nao_gosta', 'nao_pode', 'obrigatorio']

    # Inicializa estrutura vazia - padrão é aceitar tudo
    preferencias = {dia: {ref: {tp: [] for tp in tipos} for ref in refeicoes} for dia in dias}

    try:
        with open(arquivo_preferencias, 'r', encoding='utf-8') as arquivo:
            for linha in arquivo:
                linha = linha.strip()
                if linha and not linha.startswith('#'):  # Ignora linhas vazias e comentários
                    partes = linha.split(',')
                    if len(partes) >= 3:  # Mínimo: dia, refeicao, tipo
                        dia = partes[0].strip().lower()
                        refeicao = partes[1].strip().lower()
                        tipo = partes[2].strip().lower()

                        # Se há alimentos especificados
                        if len(partes) > 3:
                            try:
                                alimentos = [int(x.strip()) for x in partes[3:] if x.strip()]
                            except ValueError:
                                print(f"Aviso: Números de alimentos inválidos na linha: {linha}")
                                continue
                        else:
                            alimentos = []

                        # Verifica se dia, refeição e tipo são válidos
                        if dia in preferencias and refeicao in preferencias[dia] and tipo in preferencias[dia][refeicao]:
                            preferencias[dia][refeicao][tipo] = alimentos
                        else:
                            print(f"Aviso: Linha ignorada (dia/refeição/tipo inválido): {linha}")

    except FileNotFoundError:
        print("Arquivo de preferências não encontrado. Usando sistema padrão (aceita tudo).")
    except Exception as e:
        print(f"Erro ao carregar preferências: {e}. Usando sistema padrão (aceita tudo).")

    return preferencias

def gerar_refeicao(taco, preferencias_refeicao, calorias_refeicao):
    """Gera uma refeição com base nas preferências e restrições."""
    obrigatorios = preferencias_refeicao.get('obrigatorio', [])
    nao_pode = set(preferencias_refeicao.get('nao_pode', []))
    gosta = preferencias_refeicao.get('gosta', [])

    # Todos os alimentos disponíveis (1 até o número total de alimentos)
    todos_alimentos = list(range(1, len(taco) + 1))

    # Remove apenas os que não pode comer
    alimentos_permitidos = [i for i in todos_alimentos if i not in nao_pode]

    # Remove obrigatórios da lista de permitidos para não duplicar
    alimentos_para_completar = [i for i in alimentos_permitidos if i not in obrigatorios]

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
                'obrigatorio': True
            })

            calorias_acumuladas += (alimento['caloriaskcal'] / 100) * proporcao
            proteinas_acumuladas += (alimento['proteig'] / 100) * proporcao
            gorduras_acumuladas += (alimento['gordurag'] / 100) * proporcao
            carboidratos_acumulados += (alimento['caarboidratog'] / 100) * proporcao

    # Depois, completa com outros alimentos até atingir as calorias desejadas
    tentativas = 0
    max_tentativas = 50  # Evita loop infinito

    while calorias_acumuladas < calorias_refeicao * 0.9 and alimentos_usaveis and tentativas < max_tentativas:
        alimento_id = random.choice(alimentos_usaveis)
        alimento = taco.iloc[alimento_id - 1]

        if alimento['caloriaskcal'] > 0:
            calorias_restantes = calorias_refeicao - calorias_acumuladas
            proporcao = min(100, max(10, calorias_restantes / alimento['caloriaskcal'] * 100))
        else:
            proporcao = 30  # Valor padrão para alimentos sem calorias

        refeicao.append({
            'descricao': alimento['descricao'],
            'proporcao': proporcao,
            'obrigatorio': False
        })

        calorias_acumuladas += (alimento['caloriaskcal'] / 100) * proporcao
        proteinas_acumuladas += (alimento['proteig'] / 100) * proporcao
        gorduras_acumuladas += (alimento['gordurag'] / 100) * proporcao
        carboidratos_acumulados += (alimento['caarboidratog'] / 100) * proporcao

        # Remove o alimento usado para não repeti-lo
        alimentos_usaveis.remove(alimento_id)
        tentativas += 1

    return refeicao, calorias_acumuladas, proteinas_acumuladas, gorduras_acumuladas, carboidratos_acumulados

def gerar_plano_dieta(taco, preferencias, calorias_semana):
    """Gera um plano de dieta completo para a semana."""
    dias = ['seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom']
    refeicoes = ['cafe_da_manha', 'lanche_da_manha', 'almoco', 'lanche_da_tarde', 'jantar']

    plano_semana = {}
    totais_semana = {}

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

        plano_dia = {}
        total_calorias = total_proteinas = total_gorduras = total_carboidratos = 0

        for refeicao in refeicoes:
            alimentos, calorias, proteinas, gorduras, carboidratos = gerar_refeicao(
                taco, preferencias[dia][refeicao], calorias_refeicoes[refeicao]
            )

            plano_dia[refeicao] = alimentos
            total_calorias += calorias
            total_proteinas += proteinas
            total_gorduras += gorduras
            total_carboidratos += carboidratos

        plano_semana[dia] = plano_dia
        totais_semana[dia] = {
            'calorias': total_calorias,
            'proteinas': total_proteinas,
            'gorduras': total_gorduras,
            'carboidratos': total_carboidratos
        }

    return plano_semana, totais_semana

def imprimir_plano_semana(plano_semana, totais_semana):
    """Imprime o plano de dieta semanal de forma organizada."""
    dias = ['seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom']

    print("\n" + "="*80)
    print("PLANO DE DIETA SEMANAL PERSONALIZADO")
    print("="*80)

    for dia in dias:
        print(f"\n{'='*20} {dia.upper()} {'='*20}")

        for refeicao, alimentos in plano_semana[dia].items():
            print(f"\n{refeicao.replace('_', ' ').title()}:")

            if alimentos:
                for alimento in alimentos:
                    marcador = "★" if alimento.get('obrigatorio', False) else "•"
                    print(f"  {marcador} {alimento['descricao']} ({alimento['proporcao']:.1f}g)")
            else:
                print("  • Sem opções disponíveis com as restrições informadas.")

        print(f"\nTotais do dia:")
        print(f"  Calorias: {totais_semana[dia]['calorias']:.1f} kcal")
        print(f"  Proteínas: {totais_semana[dia]['proteinas']:.1f} g")
        print(f"  Gorduras: {totais_semana[dia]['gorduras']:.1f} g")
        print(f"  Carboidratos: {totais_semana[dia]['carboidratos']:.1f} g")

def salvar_plano_arquivo(plano_semana, totais_semana, nome_arquivo="plano_dieta_semanal.txt"):
    """Salva o plano de dieta em um arquivo de texto."""
    dias = ['seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom']

    with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
        arquivo.write("PLANO DE DIETA SEMANAL PERSONALIZADO\n")
        arquivo.write("="*80 + "\n")

        for dia in dias:
            arquivo.write(f"\n{'='*20} {dia.upper()} {'='*20}\n")

            for refeicao, alimentos in plano_semana[dia].items():
                arquivo.write(f"\n{refeicao.replace('_', ' ').title()}:\n")

                if alimentos:
                    for alimento in alimentos:
                        marcador = "★" if alimento.get('obrigatorio', False) else "•"
                        arquivo.write(f"  {marcador} {alimento['descricao']} ({alimento['proporcao']:.1f}g)\n")
                else:
                    arquivo.write("  • Sem opções disponíveis com as restrições informadas.\n")

            arquivo.write(f"\nTotais do dia:\n")
            arquivo.write(f"  Calorias: {totais_semana[dia]['calorias']:.1f} kcal\n")
            arquivo.write(f"  Proteínas: {totais_semana[dia]['proteinas']:.1f} g\n")
            arquivo.write(f"  Gorduras: {totais_semana[dia]['gorduras']:.1f} g\n")
            arquivo.write(f"  Carboidratos: {totais_semana[dia]['carboidratos']:.1f} g\n")

    print(f"\nPlano de dieta salvo em: {nome_arquivo}")

def main():
    """Função principal do sistema."""
    print("Sistema de Geração de Dieta Personalizada - TACO")
    print("="*50)

    # Carregar dados
    arquivo_taco = 'TACO_Base_Paula.csv'
    arquivo_preferencias = 'preferencias.txt'

    print("Carregando tabela TACO...")
    taco = carregar_taco(arquivo_taco)
    print(f"Tabela TACO carregada: {len(taco)} alimentos disponíveis")

    print("\nCarregando preferências...")
    preferencias = carregar_preferencias(arquivo_preferencias)
    print("Preferências carregadas (sistema por exceção - aceita tudo por padrão)")

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
    plano_semana, totais_semana = gerar_plano_dieta(taco, preferencias, calorias_semana)

    # Imprimir resultado
    imprimir_plano_semana(plano_semana, totais_semana)

    # Salvar em arquivo
    salvar_plano_arquivo(plano_semana, totais_semana)

    print("\n" + "="*80)
    print("★ = Alimento obrigatório")
    print("• = Alimento sugerido")
    print("="*80)

if __name__ == "__main__":
    main()
