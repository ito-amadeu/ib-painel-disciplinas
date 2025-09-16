import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import pytz

# Configura o timezone de Brasília
tz = pytz.timezone("America/Sao_Paulo")

# Carrega os dados
df = pd.read_csv("disciplinas_ib.csv")

# Garante que os horários sejam strings formatadas corretamente
df["inicio"] = pd.to_datetime(df["inicio"], format="%H:%M").dt.strftime("%H:%M")
df["fim"] = pd.to_datetime(df["fim"], format="%H:%M").dt.strftime("%H:%M")

# Agora datetime com timezone
def to_datetime_today(hora_str):
    return tz.localize(datetime.combine(datetime.now(tz).date(), 
                                        datetime.strptime(hora_str, "%H:%M").time()))

df["inicio_dt"] = df["inicio"].apply(to_datetime_today)
df["fim_dt"] = df["fim"].apply(to_datetime_today)

# Agora "now" também no fuso correto
now = datetime.now(tz)

# Calcula tempo restante ou até começar
def calcula_tempo(row):
    if row["inicio_dt"] <= now < row["fim_dt"]:
        delta = row["fim_dt"] - now
        horas, resto = divmod(delta.seconds, 3600)
        minutos = resto // 60
        return f"{horas}h {minutos}min restantes"
    elif now < row["inicio_dt"]:
        delta = row["inicio_dt"] - now
        horas, resto = divmod(delta.seconds, 3600)
        minutos = resto // 60
        return f"começa em {horas}h {minutos}min"
    else:
        return None  # já encerrada

df["tempo"] = df.apply(calcula_tempo, axis=1)

# Remove as encerradas
df = df.dropna(subset=["tempo"])

# Reordena colunas
df = df[["codigo", "sala", "turma", "nome", "inicio", "fim", "tempo"]]

# Função para separar períodos
def periodo(hora_str):
    h = int(hora_str.split(":")[0])
    if 7 <= h < 12:
        return "🌅 Manhã"
    elif 12 <= h < 18:
        return "🌇 Tarde"
    else:
        return "🌙 Noite"

df["período"] = df["inicio"].apply(periodo)

# Layout no Streamlit
st.title("📚 Painel de Disciplinas - IB Unicamp")

for periodo_nome, grupo in df.groupby("período"):
    st.subheader(periodo_nome)
    # Garante formatação monoespaçada em colunas específicas
    styled = grupo.style.set_properties(
        subset=["codigo", "sala", "turma", "inicio", "fim"],
        **{"font-family": "monospace"}
    )
    st.table(styled.hide(axis="index"))
