import pandas as pd
import streamlit as st
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 🔄 Auto-refresh a cada 60 segundos
st_autorefresh(interval=60 * 1000, key="refresh")

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

# Função para calcular status e tempo restante
def calcular_status(row):
    agora = datetime.now(tz)
    inicio = datetime.strptime(row["inicio"], "%H:%M").replace(
        year=agora.year, month=agora.month, day=agora.day, tzinfo=tz
    )
    fim = datetime.strptime(row["fim"], "%H:%M").replace(
        year=agora.year, month=agora.month, day=agora.day, tzinfo=tz
    )

    if inicio <= agora <= fim:
        minutos = int((fim - agora).total_seconds() // 60)
        return f"⏳ {minutos} min restantes"
    elif agora < inicio:
        minutos = int((inicio - agora).total_seconds() // 60)
        return f"🕒 começa em {minutos} min"
    else:
        return "✅ Encerrada"

st.title("📚 Painel de Disciplinas - IB Unicamp")

# Filtra disciplinas de hoje
disciplinas = disciplinas_do_dia().copy()

if disciplinas.empty:
    st.warning("Nenhuma disciplina encontrada para hoje 📭")
else:
    disciplinas["periodo"] = disciplinas["inicio"].apply(classificar_periodo)
    disciplinas["status"] = disciplinas.apply(calcular_status, axis=1)

    # Exibe por período em colunas
    col1, col2, col3 = st.columns(3)
    periodos = [("🌅 Manhã", col1), ("🌇 Tarde", col2), ("🌙 Noite", col3)]

    for periodo, col in periodos:
        subset = disciplinas[disciplinas["periodo"] == periodo]
        if not subset.empty:
            with col:
                st.subheader(periodo)
                st.dataframe(subset[["codigo", "nome", "turma", "inicio", "fim", "sala", "status"]])

