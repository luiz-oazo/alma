import streamlit as st
import pyotp
import qrcode
import io

# =========================
# CONFIG AUTH
# =========================

SECRET = "JBSWY3DPEHPK3PXP"  # você pode gerar outro

totp = pyotp.TOTP(SECRET)

# =========================
# LOGIN
# =========================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Login Seguro")

    st.write("Use seu Google Authenticator")

    code = st.text_input("Digite o código:", type="password")

    if st.button("Entrar"):
        if totp.verify(code):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Código inválido ❌")

    # QR Code para configurar no celular
    st.write("📱 Configure no Google Authenticator:")

    uri = pyotp.totp.TOTP(SECRET).provisioning_uri(
        name="DISC App",
        issuer_name="Luiz App"
    )


    qr = qrcode.make(uri)

    buf = io.BytesIO()
    qr.save(buf, format="PNG")

    st.image(buf.getvalue())

    st.stop()

# =========================
# APP PRINCIPAL (SEU CÓDIGO)
# =========================

st.set_page_config(page_title="Teste DISC", layout="centered")

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

st.title("🧠 Teste DISC")
st.progress(st.session_state.q / len(questions))

q = st.session_state.q

if q < len(questions):

    st.subheader(f"Pergunta {q+1}")
    choice = st.radio("Costumo ser:", questions[q])

    col1, col2 = st.columns(2)

    if col1.button("⬅ Voltar"):
        if q > 0:
            prev = st.session_state.answers[q-1]
            if prev is not None:
                st.session_state.scores[disc_map[prev]] -= 1
            st.session_state.q -= 1
            st.rerun()

    if col2.button("Próximo ➡"):
        idx = questions[q].index(choice)

        if st.session_state.answers[q] is not None:
            old = st.session_state.answers[q]
            st.session_state.scores[disc_map[old]] -= 1

        st.session_state.answers[q] = idx
        st.session_state.scores[disc_map[idx]] += 1

        st.session_state.q += 1
        st.rerun()

else:
    st.success("Finalizado!")

    st.bar_chart(st.session_state.scores)

    perfil = max(st.session_state.scores, key=st.session_state.scores.get)

    st.write(f"Perfil: {perfil}")
