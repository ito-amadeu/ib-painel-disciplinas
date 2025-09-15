import pandas as pd
import streamlit as st
import time
from datetime import datetime
import pytz

# Configura fuso horário de Brasília
tz = pytz.timezone("America/Sao_Paulo")

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

# 🔄 Atualiza a cada 60 segundos
time.sleep(60)
st.experimental_rerun()
