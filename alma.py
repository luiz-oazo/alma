import tkinter as tk

# Perguntas
questions = [
    ["Confiante", "Consistente", "Determinado", "Preciso"],
    ["Político", "Cooperativo", "Competitivo", "Diplomata"],
    ["Otimista", "Paciente", "Assertivo", "Prudente"],
    ["Expansivo", "Possessivo", "Agressivo", "Julgador"],
    ["Comunicativo", "Agradável", "Inovador", "Elegante"],
    ["Entusiasmado", "Calmo", "Enérgico", "Disciplinado"],
    ["Criativo", "Ponderado", "Visionário", "Detalhista"],
    ["Convincente", "Compreensivo", "Confiável", "Pontual"],
    ["Sedutor", "Harmonizador", "Ousado", "Cauteloso"],
    ["Sociável", "Leal", "Exigente", "Rigoroso"],
    ["Reluzente", "Regulado", "Ambicioso", "Calculista"],
    ["Persuasivo", "Metódico", "Apressado", "Preciso"],
    ["Exagerado", "Estável", "Objetivo", "Exato"],
    ["Inspirador", "Persistente", "Fazedor", "Perfeccionista"],
    ["Flexível", "Previsível", "Decidido", "Sistemático"],
    ["Extravagante", "Modesto", "Autoritário", "Dependente"],
    ["Expressivo", "Amável", "Firme", "Formal"],
    ["Caloroso", "Gentil", "Vigoroso", "Preocupado"],
    ["Espontâneo", "Energético", "Satisfeito", "Conservador"],
    ["Divertido", "Tranquilo", "Pioneiro", "Convencional"],
    ["Dado", "Rígido consigo", "Inquisitivo", "Cético"],
    ["Extrovertido", "Casual", "Audacioso", "Meticuloso"],
    ["Jovial", "Moderado", "Direto", "Processual"],
    ["Tagarela", "Acomodado", "Egocêntrico", "Dependente"]
]

disc_map = ["I", "S", "D", "C"]
scores = {"I": 0, "S": 0, "D": 0, "C": 0}
answers = [None] * len(questions)

current = 0

# Função ao clicar
def answer_question(choice):
    global current

    # remove pontuação anterior
    if answers[current] is not None:
        old = disc_map[answers[current]]
        scores[old] -= 1

    answers[current] = choice
    scores[disc_map[choice]] += 1

    current += 1

    if current < len(questions):
        show_question()
    else:
        show_result()

# Voltar
def go_back():
    global current
    if current > 0:
        current -= 1
        prev = answers[current]
        if prev is not None:
            scores[disc_map[prev]] -= 1
        show_question()

# Mostrar pergunta
def show_question():
    for widget in frame.winfo_children():
        widget.destroy()

    label = tk.Label(frame, text=f"Pergunta {current+1}: Costumo ser...", font=("Arial", 14))
    label.pack(pady=10)

    for i, option in enumerate(questions[current]):
        btn = tk.Button(frame, text=option, width=30,
                        command=lambda i=i: answer_question(i))
        btn.pack(pady=5)

    back_btn = tk.Button(frame, text="⬅ Voltar", command=go_back)
    back_btn.pack(pady=10)

# Resultado
def show_result():
    for widget in frame.winfo_children():
        widget.destroy()

    result_text = "RESULTADO:\n\n"
    for k, v in scores.items():
        result_text += f"{k}: {v}\n"

    perfil = max(scores, key=scores.get)

    interpretacao = {
        "I": "Influência (comunicativo, expansivo, sociável)",
        "S": "Estabilidade (calmo, paciente, cooperativo)",
        "D": "Dominância (decidido, assertivo, competitivo)",
        "C": "Conformidade (analítico, detalhista, preciso)"
    }

    result_text += f"\nPerfil: {perfil}\n{interpretacao[perfil]}"

    label = tk.Label(frame, text=result_text, font=("Arial", 14))
    label.pack(pady=20)

# Interface
root = tk.Tk()
root.title("Teste DISC")

frame = tk.Frame(root)
frame.pack(padx=20, pady=20)

show_question()

root.mainloop()
