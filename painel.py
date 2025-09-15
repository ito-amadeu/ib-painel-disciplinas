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

# Função para formatar duração em horas e minutos
def formatar_tempo(delta):
    total_min = int(delta.total_seconds() // 60)
    horas, minutos = divmod(total_min, 60)
    if horas > 0:
        return f"{horas}h {minutos}min"
    else:
        return f"{minutos}min"

# Função para calcular status
def calcular_status(row):
    agora = datetime.now(tz)
    inicio = datetime.strptime(row["inicio"], "%H:%M").replace(
        year=agora.year, month=agora.month, day=agora.day, tzinfo=tz
    )
    fim = datetime.strptime(row["fim"], "%H:%M").replace(
        year=agora.year, month=agora.month, day=agora.day, tzinfo=tz
    )

    if inicio <= agora <= fim:
        return "andamento", f"⏳ {formatar_tempo(fim - agora)} restantes"
    elif agora < inicio:
        return "futuro", f"🕒 começa em {formatar_tempo(inicio - agora)}"
    else:
        return "encerrada", None

st.title("📚 Disciplinas - IB Unicamp")

# Filtra disciplinas de hoje
disciplinas = disciplinas_do_dia().copy()

if disciplinas.empty:
    st.warning("Nenhuma disciplina encontrada para hoje 📭")
else:
    disciplinas["periodo"] = disciplinas["inicio"].apply(classificar_periodo)
    disciplinas[["categoria", "status"]] = disciplinas.apply(
        calcular_status, axis=1, result_type="expand"
    )

    # Mantém só em andamento e futuras
    disciplinas = disciplinas[disciplinas["categoria"] != "encerrada"]

    # Exibe por período (empilhados)
    for periodo in ["🌅 Manhã", "🌇 Tarde", "🌙 Noite"]:
        subset = disciplinas[disciplinas["periodo"] == periodo]
        if not subset.empty:
            st.subheader(periodo)

            andamento = subset[subset["categoria"] == "andamento"]
            futuro = subset[subset["categoria"] == "futuro"]

            if not andamento.empty:
                st.markdown("### ⏳ Em andamento")
                st.table(
                    andamento.reset_index(drop=True)[
                        ["codigo", "nome", "turma", "inicio", "fim", "sala", "status"]
                    ]
                )

            if not futuro.empty:
                st.markdown("### 🕒 Próximas")
                st.table(
                    futuro.reset_index(drop=True)[
                        ["codigo", "nome", "turma", "inicio", "fim", "sala", "status"]
                    ]
                )

