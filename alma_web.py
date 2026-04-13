import webbrowser
import streamlit as st
import urllib.parse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import base64

st.set_page_config(page_title="Teste DISC", layout="centered")

# =========================
# INPUT INICIAL
# =========================
if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    st.title("🧠 Teste Paula Nutri ALMA")

    name = st.text_input("Seu nome:")

    if st.button("Iniciar"):
        if name:
            st.session_state.name = name
            st.session_state.started = True
            st.rerun()
        else:
            st.warning("Preencha todos os campos")

    st.stop()

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

if "q" not in st.session_state:
    st.session_state.q = 0
    st.session_state.answers = [None] * len(questions)
    st.session_state.scores = {"I": 0, "S": 0, "D": 0, "C": 0}

# =========================
# UI
# =========================
st.title(f"👤 {st.session_state.name}")
st.progress(st.session_state.q / len(questions))

q = st.session_state.q

if q < len(questions):

    st.subheader(f"Pergunta {q+1}")

    choice = st.radio("Costumo ser:", questions[q])

    if st.button("Próximo"):
        idx = questions[q].index(choice)

        if st.session_state.answers[q] is not None:
            old = st.session_state.answers[q]
            st.session_state.scores[disc_map[old]] -= 1

        st.session_state.answers[q] = idx
        st.session_state.scores[disc_map[idx]] += 1

        st.session_state.q += 1
        st.rerun()

# =========================
# RESULTADO
# =========================
else:
    scores = st.session_state.scores
    perfil = max(scores, key=scores.get)

    st.success(f"Seu perfil é: {perfil}")

    I = scores.get("I", 0)
    S = scores.get("S", 0)
    D = scores.get("D", 0)
    C = scores.get("C", 0)

    # =========================
    # GERAR PDF
    # =========================
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    c.drawString(100, 750, "Resultado DISC")
    c.drawString(100, 720, f"Nome: {st.session_state.name}")
    c.drawString(100, 690, f"Perfil: {perfil}")

    y = 650
    for k, v in scores.items():
        c.drawString(100, y, f"{k}: {v}")
        y -= 20

    c.save()
    buffer.seek(0)

    # =========================
    # LINK PARA DOWNLOAD
    # =========================
    b64 = base64.b64encode(buffer.read()).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="resultado.pdf">Download PDF</a>'

    st.markdown(href, unsafe_allow_html=True)

    # =========================
    # WHATSAPP AUTO
    # =========================

    mensagem = f"Olá {st.session_state.name}, seu perfil ALMA: I-{I} S-{S} D-{D} C-{C}."
    link = f"https://wa.me/5511983166681?text={urllib.parse.quote(mensagem)}"

    st.info("Clique abaixo para abrir o WhatsApp:")

    st.markdown(f"""
    <a href="{link}" target="_blank">
        <button style="
            background-color:#25D366;
            color:white;
            padding:12px 20px;
            border:none;
            border-radius:8px;
            font-size:16px;
            cursor:pointer;">
            💬 Abrir WhatsApp
        </button>
    </a>
    """, unsafe_allow_html=True)

