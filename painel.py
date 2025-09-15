import pandas as pd
import streamlit as st
from datetime import datetime
import pytz

# Configura fuso horário de Brasília
tz = pytz.timezone("America/Sao_Paulo")

# 🔄 Auto-refresh a cada 60 segundos
st_autorefresh = st.experimental_memo  # fallback se versão antiga
if hasattr(st, "autorefresh"):
    st_autorefresh = st.autorefresh

st_autorefresh(interval=60 * 1000, key="refresh")

# Carrega a planilha
df = pd.read_csv("disciplinas_ib.csv")

# Função para obter disciplinas do dia atual
def disciplinas_do_dia():
    hoje = datetime.now(tz).strftime("%A")
    mapa_dias = {
        "Monday": "Segunda", "Tuesday": "Terça", "Wednesday": "Quarta",
        "Thursday": "Quinta", "Friday": "Sexta", "Saturday": "Sábado",
        "Sunday": "Domingo"
    }
    return df[df["dia"] == mapa_dias[hoje]]

# Função para classificar em períodos
def classificar_periodo(hora):
    if hora < "12:00":
        return "🌅 Manhã"
    elif hora < "18:00":
        return "🌇 Tarde"
    else:
        return "🌙 Noite"

st.title("📚 Painel de Disciplinas - IB Unicamp")

# Filtra disciplinas de hoje
disciplinas = disciplinas_do_dia().copy()

if disciplinas.empty:
    st.warning("Nenhuma disciplina encontrada para hoje 📭")
else:
    disciplinas["periodo"] = disciplinas["inicio"].apply(classificar_periodo)

    # Exibe por período
    for periodo in ["🌅 Manhã", "🌇 Tarde", "🌙 Noite"]:
        subset = disciplinas[disciplinas["periodo"] == periodo]
        if not subset.empty:
            st.subheader(periodo)
            st.dataframe(subset[["codigo", "nome", "turma", "inicio", "fim", "sala"]])

