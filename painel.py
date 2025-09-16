import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz

# Configuração inicial
st.set_page_config(page_title="Painel de Disciplinas - IB Unicamp", layout="wide")

# Força refresh a cada 60s
st_autorefresh = st.experimental_rerun if hasattr(st, "experimental_rerun") else None
st.write(
    f"<meta http-equiv='refresh' content='60'>", unsafe_allow_html=True
)

# Fuso horário
tz = pytz.timezone("America/Sao_Paulo")
now = datetime.now(tz)

# Leitura do CSV
df = pd.read_csv("disciplinas_ib.csv")

# Converte colunas de tempo
df["inicio"] = pd.to_datetime(df["inicio"], format="%H:%M").dt.time
df["fim"] = pd.to_datetime(df["fim"], format="%H:%M").dt.time

# Filtro para o dia atual
dia_semana = now.strftime("%A")
dias_map = {
    "Monday": "Segunda",
    "Tuesday": "Terça",
    "Wednesday": "Quarta",
    "Thursday": "Quinta",
    "Friday": "Sexta",
    "Saturday": "Sábado",
    "Sunday": "Domingo",
}
df = df[df["dia"] == dias_map[dia_semana]]

# Funções auxiliares
def get_datetime(time_obj):
    return tz.localize(datetime.combine(now.date(), time_obj))

def format_timedelta(td):
    total_minutes = int(td.total_seconds() // 60)
    horas, minutos = divmod(total_minutes, 60)
    return f"{horas}h {minutos:02d}min"

# Processa disciplinas
disciplinas_andamento = []
disciplinas_proximas = []

for _, row in df.iterrows():
    inicio_dt = get_datetime(row["inicio"])
    fim_dt = get_datetime(row["fim"])

    if inicio_dt <= now < fim_dt:
        tempo_restante = format_timedelta(fim_dt - now)
        disciplinas_andamento.append({
            "codigo": row["codigo"],
            "sala": f"⧉ {row['sala']}",
            "turma": row["turma"],
            "nome": row["nome"],
            "inicio": inicio_dt.strftime("%H:%M"),
            "fim": fim_dt.strftime("%H:%M"),
            "tempo restante": tempo_restante,
        })
    elif inicio_dt > now:
        comeca_em = format_timedelta(inicio_dt - now)
        disciplinas_proximas.append({
            "codigo": row["codigo"],
            "sala": f"⧉ {row['sala']}",
            "turma": row["turma"],
            "nome": row["nome"],
            "inicio": inicio_dt.strftime("%H:%M"),
            "fim": fim_dt.strftime("%H:%M"),
            "começa em": comeca_em,
        })

# Separação por período
def periodo(hora):
    if 7 <= hora < 12:
        return "🌅 Manhã"
    elif 12 <= hora < 18:
        return "🌞 Tarde"
    else:
        return "🌙 Noite"

disciplinas_andamento = pd.DataFrame(disciplinas_andamento)
disciplinas_proximas = pd.DataFrame(disciplinas_proximas)

if not disciplinas_andamento.empty:
    disciplinas_andamento["período"] = pd.to_datetime(disciplinas_andamento["inicio"], format="%H:%M").dt.hour.map(periodo)
if not disciplinas_proximas.empty:
    disciplinas_proximas["período"] = pd.to_datetime(disciplinas_proximas["inicio"], format="%H:%M").dt.hour.map(periodo)

# Exibição
st.title(f"📚 Painel de Disciplinas - IB Unicamp | ⏰ {now.strftime('%H:%M')}")

with st.expander("📌 Disciplinas em andamento", expanded=True):
    for periodo_nome in ["🌅 Manhã", "🌞 Tarde", "🌙 Noite"]:
        subset = disciplinas_andamento[disciplinas_andamento["período"] == periodo_nome]
        if not subset.empty:
            st.subheader(periodo_nome)
            st.table(subset.drop(columns=["período"]))

with st.expander("⏭️ Próximas disciplinas", expanded=True):
    for periodo_nome in ["🌅 Manhã", "🌞 Tarde", "🌙 Noite"]:
        subset = disciplinas_proximas[disciplinas_proximas["período"] == periodo_nome]
        if not subset.empty:
            st.subheader(periodo_nome)
            st.table(subset.drop(columns=["período"]))
