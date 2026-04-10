import streamlit as st

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Teste DISC", layout="centered")

# =========================
# PERGUNTAS
# =========================
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

# =========================
# SESSION STATE
# =========================
if "q" not in st.session_state:
    st.session_state.q = 0
    st.session_state.answers = [None] * len(questions)
    st.session_state.scores = {"I": 0, "S": 0, "D": 0, "C": 0}

# =========================
# UI
# =========================
st.title("🧠 Teste Comportamental DISC")
st.progress((st.session_state.q) / len(questions))

q = st.session_state.q

# =========================
# PERGUNTAS
# =========================
if q < len(questions):

    st.subheader(f"Pergunta {q+1} de {len(questions)}")
    st.write("**Costumo ser...**")

    choice = st.radio(
        "Escolha uma opção:",
        questions[q],
        index=st.session_state.answers[q] if st.session_state.answers[q] is not None else 0
    )

    col1, col2 = st.columns(2)

    # VOLTAR
    if col1.button("⬅ Voltar"):
        if q > 0:
            prev = st.session_state.answers[q-1]
            if prev is not None:
                st.session_state.scores[disc_map[prev]] -= 1
            st.session_state.q -= 1
            st.rerun()

    # PRÓXIMO
    if col2.button("Próximo ➡"):
        idx = questions[q].index(choice)

        # remove resposta anterior se existir
        if st.session_state.answers[q] is not None:
            old = st.session_state.answers[q]
            st.session_state.scores[disc_map[old]] -= 1

        # salva nova resposta
        st.session_state.answers[q] = idx
        st.session_state.scores[disc_map[idx]] += 1

        st.session_state.q += 1
        st.rerun()

# =========================
# RESULTADO
# =========================
else:
    st.success("✅ Questionário finalizado!")

    scores = st.session_state.scores

    st.subheader("📊 Resultado")

    st.bar_chart(scores)

    perfil = max(scores, key=scores.get)

    interpretacao = {
        "I": "Influência (comunicativo, expansivo, sociável)",
        "S": "Estabilidade (calmo, paciente, cooperativo)",
        "D": "Dominância (decidido, assertivo, competitivo)",
        "C": "Conformidade (analítico, detalhista, preciso)"
    }

    st.markdown(f"## 🏆 Perfil predominante: **{perfil}**")
    st.write(interpretacao[perfil])

    if st.button("🔄 Refazer"):
        st.session_state.q = 0
        st.session_state.answers = [None] * len(questions)
        st.session_state.scores = {"I": 0, "S": 0, "D": 0, "C": 0}
        st.rerun()
