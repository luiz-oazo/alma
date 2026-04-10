
import pandas as pd
import numpy as np
import random
from datetime import datetime
import os

class SistemaDietaTACO:
    """
    Sistema de Geração de Dietas Personalizadas baseado na Tabela TACO

    Este sistema permite ao nutricionista:
    1. Carregar dados nutricionais da tabela TACO
    2. Coletar preferências do paciente (calorias, gostos, restrições)
    3. Gerar dietas balanceadas para 5 refeições diárias
    4. Salvar as dietas em arquivos
    """

    def __init__(self, arquivo_csv="TACO_Base_Paula.csv"):
        """Inicializa o sistema carregando os dados da tabela TACO"""
        self.arquivo_csv = arquivo_csv
        self.alimentos = self.carregar_dados_taco()
        self.refeicoes = {
            'Café da Manhã': {'min_calorias': 300, 'max_calorias': 500, 'max_alimentos': 4},
            'Lanche da Manhã': {'min_calorias': 100, 'max_calorias': 200, 'max_alimentos': 2},
            'Almoço': {'min_calorias': 400, 'max_calorias': 700, 'max_alimentos': 6},
            'Lanche da Tarde': {'min_calorias': 100, 'max_calorias': 250, 'max_alimentos': 3},
            'Jantar': {'min_calorias': 350, 'max_calorias': 600, 'max_alimentos': 5}
        }

    def carregar_dados_taco(self):
        """Carrega os dados do arquivo CSV da tabela TACO"""
        try:
            # Tenta carregar o arquivo CSV
            df = pd.read_csv(self.arquivo_csv, sep=';', encoding='utf-8')

            # Limpa e padroniza os nomes das colunas
            df.columns = df.columns.str.strip()
            colunas_esperadas = ['numero', 'descricao', 'total - g', 'calorias - kcal', 
                               'protei - g', 'gordura - g', 'caarboidrato - g', 'fibra alimentar - g']

            # Renomeia as colunas para facilitar o uso
            df.columns = ['numero', 'descricao', 'total_g', 'calorias', 'proteinas', 
                         'gorduras', 'carboidratos', 'fibras']

            # Converte vírgulas para pontos nos valores numéricos
            colunas_numericas = ['calorias', 'proteinas', 'gorduras', 'carboidratos', 'fibras']
            for col in colunas_numericas:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.replace(',', '.').astype(float)

            print(f"✅ Dados carregados com sucesso! {len(df)} alimentos disponíveis.")
            return df

        except FileNotFoundError:
            print(f"❌ Arquivo {self.arquivo_csv} não encontrado!")
            print("Usando dados de exemplo...")
            return self.criar_dados_exemplo()
        except Exception as e:
            print(f"❌ Erro ao carregar arquivo: {e}")
            print("Usando dados de exemplo...")
            return self.criar_dados_exemplo()

    def criar_dados_exemplo(self):
        """Cria dados de exemplo caso o arquivo não seja encontrado"""
        dados_exemplo = {
            'numero': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
            'descricao': [
                'Arroz, integral, cozido', 'Arroz, tipo 1, cozido', 'Aveia, flocos, crua',
                'Pão, trigo, francês', 'Pão, trigo, forma, integral', 'Macarrão, trigo, cru',
                'Batata, inglesa, cozida', 'Batata, doce, cozida', 'Mandioca, cozida',
                'Brócolis, cozido', 'Cenoura, cozida', 'Couve, manteiga, crua',
                'Banana, nanica, crua', 'Maçã, Fuji, com casca, crua', 'Laranja, baía, crua',
                'Frango, peito, sem pele, cozido', 'Carne, bovina, contra-filé, grelhado',
                'Ovo, de galinha, inteiro, cozido', 'Feijão, carioca, cozido', 'Leite, de vaca, integral'
            ],
            'calorias': [124, 128, 394, 300, 253, 371, 52, 77, 125, 25, 30, 27, 92, 56, 45, 163, 194, 146, 76, 61],
            'proteinas': [2.6, 2.5, 13.9, 8.0, 9.4, 10.0, 1.2, 0.6, 0.6, 2.1, 0.8, 2.9, 1.4, 0.3, 1.0, 31.5, 35.9, 13.3, 4.8, 3.2],
            'gorduras': [1.0, 0.2, 8.5, 3.1, 3.7, 1.3, 0.0, 0.1, 0.3, 0.5, 0.2, 0.5, 0.1, 0.0, 0.1, 3.2, 4.5, 9.5, 0.5, 3.5],
            'carboidratos': [25.8, 28.1, 66.6, 58.6, 49.9, 77.9, 11.9, 18.4, 30.1, 4.4, 6.7, 4.3, 23.8, 15.2, 11.5, 0.0, 0.0, 0.6, 13.6, 4.8],
            'fibras': [2.7, 1.6, 9.1, 2.3, 6.9, 2.9, 1.3, 2.2, 1.6, 3.4, 2.6, 3.1, 1.9, 1.3, 1.1, 0.0, 0.0, 0.0, 8.5, 0.0]
        }
        return pd.DataFrame(dados_exemplo)

    def mostrar_lista_alimentos(self):
        """Mostra a lista de alimentos disponíveis"""
        print("\n" + "="*80)
        print("                    LISTA DE ALIMENTOS DISPONÍVEIS")
        print("="*80)

        for idx, alimento in self.alimentos.iterrows():
            print(f"{alimento['numero']:3d}. {alimento['descricao']:<50} ({alimento['calorias']:3.0f} kcal/100g)")

        print("="*80)

    def coletar_preferencias(self):
        """Coleta as preferências do paciente de forma interativa"""
        print("\n" + "="*80)
        print("        SISTEMA DE GERAÇÃO DE DIETAS PERSONALIZADAS")
        print("="*80)

        # Calorias diárias
        while True:
            try:
                calorias_diarias = float(input("\n📊 Digite a quantidade de calorias que o paciente precisa consumir por dia: "))
                if calorias_diarias > 0:
                    break
                else:
                    print("❌ Por favor, digite um valor positivo.")
            except ValueError:
                print("❌ Por favor, digite um número válido.")

        # Mostrar alimentos disponíveis
        self.mostrar_lista_alimentos()

        # Alimentos preferidos
        print("\n" + "="*50)
        print("           ALIMENTOS PREFERIDOS")
        print("="*50)
        print("Digite os números dos alimentos que o paciente MAIS GOSTA")
        print("(separados por vírgula, ex: 1,3,5,7)")

        while True:
            try:
                preferidos_input = input("\n💚 Números dos alimentos preferidos: ")
                if preferidos_input.strip():
                    preferidos = [int(x.strip()) for x in preferidos_input.split(',') if x.strip().isdigit()]
                    break
                else:
                    preferidos = []
                    break
            except:
                print("❌ Formato inválido. Use números separados por vírgula.")

        # Alimentos não gostados
        print("\n" + "="*50)
        print("           ALIMENTOS NÃO GOSTADOS")
        print("="*50)
        print("Digite os números dos alimentos que o paciente NÃO GOSTA")

        while True:
            try:
                nao_gostados_input = input("\n😐 Números dos alimentos não gostados (ou Enter para pular): ")
                if nao_gostados_input.strip():
                    nao_gostados = [int(x.strip()) for x in nao_gostados_input.split(',') if x.strip().isdigit()]
                    break
                else:
                    nao_gostados = []
                    break
            except:
                print("❌ Formato inválido. Use números separados por vírgula.")

        # Alimentos proibidos
        print("\n" + "="*50)
        print("           ALIMENTOS PROIBIDOS")
        print("="*50)
        print("Digite os números dos alimentos que o paciente NÃO PODE COMER")
        print("(por alergias, intolerâncias, restrições médicas, etc.)")

        while True:
            try:
                proibidos_input = input("\n🚫 Números dos alimentos proibidos (ou Enter para pular): ")
                if proibidos_input.strip():
                    proibidos = [int(x.strip()) for x in proibidos_input.split(',') if x.strip().isdigit()]
                    break
                else:
                    proibidos = []
                    break
            except:
                print("❌ Formato inválido. Use números separados por vírgula.")

        return {
            'calorias_diarias': calorias_diarias,
            'preferidos': preferidos,
            'nao_gostados': nao_gostados,
            'proibidos': proibidos
        }

    def filtrar_alimentos_disponiveis(self, preferencias):
        """Filtra alimentos baseado nas preferências e adiciona pesos"""
        # Remove alimentos proibidos
        alimentos_disponiveis = self.alimentos[
            ~self.alimentos['numero'].isin(preferencias['proibidos'])
        ].copy()

        # Adiciona peso para seleção baseado nas preferências
        alimentos_disponiveis['peso_preferencia'] = 1.0

        # Aumenta peso para alimentos preferidos
        alimentos_disponiveis.loc[
            alimentos_disponiveis['numero'].isin(preferencias['preferidos']), 
            'peso_preferencia'
        ] = 3.0

        # Reduz peso para alimentos não gostados
        alimentos_disponiveis.loc[
            alimentos_disponiveis['numero'].isin(preferencias['nao_gostados']), 
            'peso_preferencia'
        ] = 0.3

        return alimentos_disponiveis

    def gerar_refeicao(self, nome_refeicao, calorias_alvo, alimentos_disponiveis):
        """Gera uma refeição específica"""
        config_refeicao = self.refeicoes[nome_refeicao]
        max_alimentos = config_refeicao['max_alimentos']

        alimentos_selecionados = []
        calorias_total = 0
        tentativas = 0
        max_tentativas = 100
        alimentos_usados = set()

        while (calorias_total < calorias_alvo * 0.8 and 
               len(alimentos_selecionados) < max_alimentos and 
               tentativas < max_tentativas):

            # Filtra alimentos não usados nesta refeição
            alimentos_nao_usados = alimentos_disponiveis[
                ~alimentos_disponiveis['numero'].isin(alimentos_usados)
            ]

            if len(alimentos_nao_usados) == 0:
                break

            # Seleciona alimento com base no peso de preferência
            weights = alimentos_nao_usados['peso_preferencia'].values
            if weights.sum() == 0:
                break

            # Seleção aleatória ponderada
            alimento_idx = np.random.choice(len(alimentos_nao_usados), p=weights/weights.sum())
            alimento = alimentos_nao_usados.iloc[alimento_idx]

            # Define quantidade baseada no tipo de refeição
            if nome_refeicao in ['Lanche da Manhã', 'Lanche da Tarde']:
                quantidade = random.randint(30, 100)  # Porções menores para lanches
            else:
                quantidade = random.randint(50, 200)  # Porções maiores para refeições principais

            calorias_alimento = (alimento['calorias'] * quantidade) / 100

            # Verifica se não ultrapassa muito o limite
            if calorias_total + calorias_alimento <= calorias_alvo * 1.3:
                alimentos_selecionados.append({
                    'alimento': alimento['descricao'],
                    'quantidade': quantidade,
                    'calorias': calorias_alimento,
                    'proteinas': (alimento['proteinas'] * quantidade) / 100,
                    'gorduras': (alimento['gorduras'] * quantidade) / 100,
                    'carboidratos': (alimento['carboidratos'] * quantidade) / 100,
                    'fibras': (alimento['fibras'] * quantidade) / 100
                })
                calorias_total += calorias_alimento
                alimentos_usados.add(alimento['numero'])

            tentativas += 1

        return alimentos_selecionados, calorias_total

    def gerar_dieta_completa(self, preferencias):
        """Gera uma dieta completa para o dia"""
        calorias_diarias = preferencias['calorias_diarias']
        alimentos_disponiveis = self.filtrar_alimentos_disponiveis(preferencias)

        # Distribui calorias pelas refeições
        distribuicao_calorias = {
            'Café da Manhã': calorias_diarias * 0.25,    # 25%
            'Lanche da Manhã': calorias_diarias * 0.10,  # 10%
            'Almoço': calorias_diarias * 0.35,           # 35%
            'Lanche da Tarde': calorias_diarias * 0.10,  # 10%
            'Jantar': calorias_diarias * 0.20            # 20%
        }

        dieta_completa = {}
        calorias_total_dia = 0

        print("\n🔄 Gerando dieta personalizada...")

        for refeicao, calorias_alvo in distribuicao_calorias.items():
            print(f"   Gerando {refeicao}...")
            alimentos_refeicao, calorias_refeicao = self.gerar_refeicao(
                refeicao, calorias_alvo, alimentos_disponiveis
            )
            dieta_completa[refeicao] = {
                'alimentos': alimentos_refeicao,
                'calorias_total': calorias_refeicao
            }
            calorias_total_dia += calorias_refeicao

        print("✅ Dieta gerada com sucesso!")
        return dieta_completa, calorias_total_dia

    def exibir_dieta(self, dieta, calorias_total):
        """Exibe a dieta formatada na tela"""
        print("\n" + "="*80)
        print("                    DIETA PERSONALIZADA")
        print("="*80)
        print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y')}")
        print(f"🔥 Calorias totais do dia: {calorias_total:.0f} kcal")
        print("="*80)

        for refeicao, dados in dieta.items():
            print(f"\n🍽️  {refeicao.upper()}")
            print("-" * 60)
            print(f"Calorias da refeição: {dados['calorias_total']:.0f} kcal")
            print()

            for i, item in enumerate(dados['alimentos'], 1):
                print(f"{i}. {item['alimento']}")
                print(f"   📏 Quantidade: {item['quantidade']}g")
                print(f"   🔥 Calorias: {item['calorias']:.1f} kcal")
                print(f"   🥩 Proteínas: {item['proteinas']:.1f}g | 🧈 Gorduras: {item['gorduras']:.1f}g")
                print(f"   🍞 Carboidratos: {item['carboidratos']:.1f}g | 🌾 Fibras: {item['fibras']:.1f}g")
                print()

        # Resumo nutricional
        self.exibir_resumo_nutricional(dieta)

    def exibir_resumo_nutricional(self, dieta):
        """Exibe resumo nutricional da dieta"""
        totais = {'calorias': 0, 'proteinas': 0, 'gorduras': 0, 'carboidratos': 0, 'fibras': 0}

        for refeicao_dados in dieta.values():
            for item in refeicao_dados['alimentos']:
                totais['calorias'] += item['calorias']
                totais['proteinas'] += item['proteinas']
                totais['gorduras'] += item['gorduras']
                totais['carboidratos'] += item['carboidratos']
                totais['fibras'] += item['fibras']

        print("\n" + "="*60)
        print("                RESUMO NUTRICIONAL DO DIA")
        print("="*60)
        print(f"🔥 Calorias totais:     {totais['calorias']:.0f} kcal")
        print(f"🥩 Proteínas totais:    {totais['proteinas']:.1f} g")
        print(f"🧈 Gorduras totais:     {totais['gorduras']:.1f} g")
        print(f"🍞 Carboidratos totais: {totais['carboidratos']:.1f} g")
        print(f"🌾 Fibras totais:       {totais['fibras']:.1f} g")
        print("="*60)

    def salvar_dieta_arquivo(self, dieta, calorias_total, preferencias, nome_arquivo=None):
        """Salva a dieta em um arquivo de texto"""
        if nome_arquivo is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"dieta_personalizada_{timestamp}.txt"

        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("                    DIETA PERSONALIZADA\n")
                f.write("="*80 + "\n")
                f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
                f.write(f"Calorias totais do dia: {calorias_total:.0f} kcal\n\n")

                # Informações do paciente
                f.write("INFORMAÇÕES DO PACIENTE:\n")
                f.write("-" * 40 + "\n")
                f.write(f"Calorias diárias necessárias: {preferencias['calorias_diarias']:.0f} kcal\n")
                f.write(f"Alimentos preferidos: {preferencias['preferidos']}\n")
                f.write(f"Alimentos não gostados: {preferencias['nao_gostados']}\n")
                f.write(f"Alimentos proibidos: {preferencias['proibidos']}\n")
                f.write("="*80 + "\n\n")

                # Dieta detalhada
                for refeicao, dados in dieta.items():
                    f.write(f"{refeicao.upper()}\n")
                    f.write("-" * 60 + "\n")
                    f.write(f"Calorias da refeição: {dados['calorias_total']:.0f} kcal\n\n")

                    for i, item in enumerate(dados['alimentos'], 1):
                        f.write(f"{i}. {item['alimento']}\n")
                        f.write(f"   Quantidade: {item['quantidade']}g\n")
                        f.write(f"   Calorias: {item['calorias']:.1f} kcal\n")
                        f.write(f"   Proteínas: {item['proteinas']:.1f}g | Gorduras: {item['gorduras']:.1f}g\n")
                        f.write(f"   Carboidratos: {item['carboidratos']:.1f}g | Fibras: {item['fibras']:.1f}g\n\n")

                    f.write("\n")

                # Resumo nutricional
                totais = {'calorias': 0, 'proteinas': 0, 'gorduras': 0, 'carboidratos': 0, 'fibras': 0}
                for refeicao_dados in dieta.values():
                    for item in refeicao_dados['alimentos']:
                        totais['calorias'] += item['calorias']
                        totais['proteinas'] += item['proteinas']
                        totais['gorduras'] += item['gorduras']
                        totais['carboidratos'] += item['carboidratos']
                        totais['fibras'] += item['fibras']

                f.write("="*60 + "\n")
                f.write("                RESUMO NUTRICIONAL DO DIA\n")
                f.write("="*60 + "\n")
                f.write(f"Calorias totais:     {totais['calorias']:.0f} kcal\n")
                f.write(f"Proteínas totais:    {totais['proteinas']:.1f} g\n")
                f.write(f"Gorduras totais:     {totais['gorduras']:.1f} g\n")
                f.write(f"Carboidratos totais: {totais['carboidratos']:.1f} g\n")
                f.write(f"Fibras totais:       {totais['fibras']:.1f} g\n")
                f.write("="*60 + "\n")

            print(f"\n✅ Dieta salva com sucesso no arquivo: {nome_arquivo}")
            return nome_arquivo

        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")
            return None

    def gerar_nova_dieta(self, preferencias):
        """Gera uma nova dieta com as mesmas preferências"""
        print("\n🔄 Gerando nova dieta com as mesmas preferências...")
        return self.gerar_dieta_completa(preferencias)

    def menu_principal(self):
        """Menu principal do sistema"""
        print("\n" + "="*80)
        print("        SISTEMA DE GERAÇÃO DE DIETAS PERSONALIZADAS - TACO")
        print("="*80)
        print("Desenvolvido para nutricionistas")
        print("Baseado na Tabela Brasileira de Composição de Alimentos (TACO)")

        while True:
            print("\n" + "="*50)
            print("                MENU PRINCIPAL")
            print("="*50)
            print("1. 🍽️  Gerar nova dieta personalizada")
            print("2. 📋 Mostrar lista de alimentos disponíveis")
            print("3. ❓ Sobre o sistema")
            print("4. 🚪 Sair")

            opcao = input("\nEscolha uma opção (1-4): ").strip()

            if opcao == '1':
                self.fluxo_gerar_dieta()
            elif opcao == '2':
                self.mostrar_lista_alimentos()
                input("\nPressione Enter para continuar...")
            elif opcao == '3':
                self.mostrar_sobre()
            elif opcao == '4':
                print("\n👋 Obrigado por usar o Sistema de Dietas TACO!")
                break
            else:
                print("❌ Opção inválida. Tente novamente.")

    def fluxo_gerar_dieta(self):
        """Fluxo completo para gerar uma dieta"""
        try:
            # Coleta preferências
            preferencias = self.coletar_preferencias()

            # Gera dieta
            dieta, calorias_total = self.gerar_dieta_completa(preferencias)

            # Exibe dieta
            self.exibir_dieta(dieta, calorias_total)

            # Menu de opções pós-geração
            while True:
                print("\n" + "="*50)
                print("                   OPÇÕES")
                print("="*50)
                print("1. 💾 Salvar dieta em arquivo")
                print("2. 🔄 Gerar nova dieta (mesmas preferências)")
                print("3. 🏠 Voltar ao menu principal")

                opcao = input("\nEscolha uma opção (1-3): ").strip()

                if opcao == '1':
                    nome_arquivo = self.salvar_dieta_arquivo(dieta, calorias_total, preferencias)
                    if nome_arquivo:
                        print(f"📁 Arquivo salvo: {nome_arquivo}")
                elif opcao == '2':
                    dieta, calorias_total = self.gerar_nova_dieta(preferencias)
                    self.exibir_dieta(dieta, calorias_total)
                elif opcao == '3':
                    break
                else:
                    print("❌ Opção inválida. Tente novamente.")

        except KeyboardInterrupt:
            print("\n\n⚠️  Operação cancelada pelo usuário.")
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")

    def mostrar_sobre(self):
        """Mostra informações sobre o sistema"""
        print("\n" + "="*80)
        print("                        SOBRE O SISTEMA")
        print("="*80)
        print("🍽️  Sistema de Geração de Dietas Personalizadas")
        print("📊 Baseado na Tabela Brasileira de Composição de Alimentos (TACO)")
        print("👨‍⚕️  Desenvolvido para auxiliar nutricionistas")
        print()
        print("FUNCIONALIDADES:")
        print("• Carregamento de dados nutricionais da tabela TACO")
        print("• Coleta de preferências e restrições do paciente")
        print("• Geração automática de dietas balanceadas")
        print("• 5 refeições diárias: Café, Lanche manhã, Almoço, Lanche tarde, Jantar")
        print("• Cálculo automático de macronutrientes")
        print("• Exportação de dietas para arquivo")
        print("• Sistema de pesos para preferências alimentares")
        print()
        print("COMO USAR:")
        print("1. Informe as calorias diárias necessárias")
        print("2. Selecione alimentos preferidos, não gostados e proibidos")
        print("3. O sistema gerará uma dieta personalizada")
        print("4. Salve a dieta em arquivo para o paciente")
        print("="*80)
        input("\nPressione Enter para continuar...")


def main():
    """Função principal para executar o sistema"""
    try:
        # Inicializa o sistema
        sistema = SistemaDietaTACO()

        # Executa o menu principal
        sistema.menu_principal()

    except Exception as e:
        print(f"❌ Erro ao inicializar o sistema: {e}")
        print("Verifique se o arquivo TACO_Base_Paula.csv está no diretório correto.")


if __name__ == "__main__":
    main()
