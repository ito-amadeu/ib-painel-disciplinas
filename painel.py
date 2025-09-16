import pandas as pd
import streamlit as st
from datetime import datetime
import pytz

# ===============================
# Configurações
# ===============================
TZ = pytz.timezone("America/Sao_Paulo")

# Lê os dados
df = pd.read_csv("disciplinas_ib.csv")

# Converte horários para datetime.time
df["inicio"] = pd.to_datetime(df["inicio"], format="%H:%M").dt.time
df["fim"] = pd.to_datetime(df["fim"], format="%H:%M").dt.time

# Hora atual
agora = datetime.now(TZ)
dia_semana = agora.strftime("%A")

# Map dias
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

# Filtra disciplinas de hoje
df = df[df["dia"] == hoje]

# Cria colunas datetime completas
df["inicio_dt"] = df["inicio"].apply(lambda t: datetime.combine(agora.date(), t, tzinfo=TZ))
df["fim_dt"] = df["fim"].apply(lambda t: datetime.combine(agora.date(), t, tzinfo=TZ))

# Funções auxiliares
def tempo_formatado(delta):
    total_min = int(delta.total_seconds() // 60)
    h, m = divmod(total_min, 60)
    return f"{h:02d}h {m:02d}m"

def classificar(row):
    if row["inicio_dt"] <= agora <= row["fim_dt"]:
        return "andamento"
    elif agora < row["inicio_dt"]:
        return "proxima"
    return "encerrada"

def periodo(row):
    h = row["inicio"].hour
    if h < 12:
        return "Manhã"
    elif h < 18:
        return "Tarde"
    return "Noite"

df["status"] = df.apply(classificar, axis=1)
df["periodo"] = df.apply(periodo, axis=1)

# Adiciona colunas dinâmicas de tempo
def info_tempo(row):
    if row["status"] == "andamento":
        return tempo_formatado(row["fim_dt"] - agora)
    elif row["status"] == "proxima":
        return tempo_formatado(row["inicio_dt"] - agora)
    return None

df["tempo"] = df.apply(info_tempo, axis=1)

# Reordena colunas
df = df[["codigo", "sala", "turma", "nome", "inicio", "fim", "tempo", "status", "periodo"]]

# Formata inicio e fim sem segundos
df["inicio"] = df["inicio"].apply(lambda t: t.strftime("%H:%M"))
df["fim"] = df["fim"].apply(lambda t: t.strftime("%H:%M"))

# ===============================
# UI
# ===============================
st.set_page_config(layout="wide")
st.title("📚 Painel de Disciplinas - IB Unicamp")
st.markdown(f"### 📅 Hoje: **{hoje}** | ⏰ Agora: {agora.strftime('%H:%M')}")

# CSS para fonte monoespaçada em colunas selecionadas
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

def df_to_styled_html(df, tempo_col):
    df = df.rename(columns={"tempo": tempo_col})
    df = df[["codigo", "sala", "turma", "nome", "inicio", "fim", tempo_col]]
    html = df.to_html(index=False, escape=False)

    # aplica fonte monoespaçada
    for col in ["codigo", "sala", "turma", "inicio", "fim"]:
        for val in df[col].astype(str).unique():
            html = html.replace(f'<td>{val}', f'<td class="mono">{val}')

    return html

# Em andamento
df_andamento = df[df["status"] == "andamento"].sort_values(by=["inicio", "codigo"])
if not df_andamento.empty:
    st.subheader("📌 Disciplinas em andamento")
    for periodo, icone in [("Manhã", "🌅"), ("Tarde", "🌇"), ("Noite", "🌙")]:
        subset = df_andamento[df_andamento["periodo"] == periodo]
        if not subset.empty:
            with st.expander(f"{icone} {periodo}", expanded=True):
                st.markdown(df_to_styled_html(subset, "Tempo restante"), unsafe_allow_html=True)
else:
    st.info("Nenhuma disciplina em andamento no momento.")

# Próximas
df_proximas = df[df["status"] == "proxima"].sort_values(by=["inicio", "codigo"])
if not df_proximas.empty:
    st.subheader("⏭️ Próximas disciplinas")
    for periodo, icone in [("Manhã", "🌅"), ("Tarde", "🌇"), ("Noite", "🌙")]:
        subset = df_proximas[df_proximas["periodo"] == periodo]
        if not subset.empty:
            with st.expander(f"{icone} {periodo}", expanded=True):
                st.markdown(df_to_styled_html(subset, "Começa em"), unsafe_allow_html=True)
else:
    st.info("Nenhuma disciplina futura para hoje.")
