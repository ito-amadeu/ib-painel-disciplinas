import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import pytz

# ===============================
# Configurações
# ===============================
TZ = pytz.timezone("America/Sao_Paulo")

# Lê os dados
df = pd.read_csv("disciplinas_ib.csv")

# Converte horários para datetime
df["inicio"] = pd.to_datetime(df["inicio"], format="%H:%M").dt.time
df["fim"] = pd.to_datetime(df["fim"], format="%H:%M").dt.time

# Obtém hora atual em SP
agora = datetime.now(TZ)
hora_atual = agora.time()
dia_semana = agora.strftime("%A")  # Ex.: 'Monday'

# Mapeamento português
dias_map = {
    "Monday": "Segunda",
    "Tuesday": "Terça",
    "Wednesday": "Quarta",
    "Thursday": "Quinta",
    "Friday": "Sexta",
    "Saturday": "Sábado",
    "Sunday": "Domingo"
}
hoje = dias_map[dia_semana]

# Filtra apenas disciplinas do dia
df = df[df["dia"] == hoje]

# Converte horários para datetime hoje
df["inicio_dt"] = df["inicio"].apply(lambda t: datetime.combine(agora.date(), t, tzinfo=TZ))
df["fim_dt"] = df["fim"].apply(lambda t: datetime.combine(agora.date(), t, tzinfo=TZ))

# Classifica status
def get_status(row):
    if row["inicio_dt"] <= agora <= row["fim_dt"]:
        return "Em andamento"
    elif agora < row["inicio_dt"]:
        return "Próxima"
    else:
        return "Encerrada"

df["status"] = df.apply(get_status, axis=1)

# Calcula tempos
def tempo_restante(row):
    if row["status"] == "Em andamento":
        delta = row["fim_dt"] - agora
        return f"{delta.seconds//3600:02d}h {(delta.seconds//60)%60:02d}m"
    elif row["status"] == "Próxima":
        delta = row["inicio_dt"] - agora
        return f"{delta.seconds//3600:02d}h {(delta.seconds//60)%60:02d}m"
    return "-"

df["tempo"] = df.apply(tempo_restante, axis=1)

# Reordena colunas
df = df[["codigo", "sala", "turma", "nome", "inicio", "fim", "status", "tempo"]]

# ===============================
# Função para estilizar colunas
# ===============================
def df_to_styled_html(df):
    html = df.to_html(index=False, escape=False)

    # aplica classe monoespaçada em certas colunas
    for col in ["codigo", "sala", "turma", "inicio", "fim"]:
        for val in df[col].astype(str).unique():
            html = html.replace(f'<td>{val}', f'<td class="mono">{val}')

    return html

# ===============================
# Streamlit UI
# ===============================
st.set_page_config(layout="wide")
st.title("📚 Painel de Disciplinas - IB Unicamp")
st.markdown(f"### 📅 Hoje: **{hoje}** | ⏰ Agora: {agora.strftime('%H:%M')}")

# CSS
st.markdown("""
    <style>
    .mono {
        font-family: monospace;
        font-size: 15px;
    }
    td, th {
        font-size: 15px;
        padding: 6px 12px;
        text-align: center;
    }
    th {
        font-weight: bold;
    }
    table {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Em andamento
df_andamento = df[df["status"] == "Em andamento"].sort_values(by=["inicio", "codigo"])
if not df_andamento.empty:
    st.subheader("📌 Disciplinas em andamento")
    st.markdown(df_to_styled_html(df_andamento), unsafe_allow_html=True)
else:
    st.info("Nenhuma disciplina em andamento no momento.")

# Próximas
df_proximas = df[df["status"] == "Próxima"].sort_values(by=["inicio", "codigo"])
if not df_proximas.empty:
    st.subheader("⏭️ Próximas disciplinas")
    st.markdown(df_to_styled_html(df_proximas), unsafe_allow_html=True)
else:
    st.info("Nenhuma disciplina futura para hoje.")
