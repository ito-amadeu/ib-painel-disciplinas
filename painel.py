import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import pytz

# ==============================
# Configuração
# ==============================
st.set_page_config(page_title="📚 Painel de Disciplinas", layout="centered")

# Carrega planilha (ajuste o nome do arquivo no Streamlit Cloud)
df = pd.read_csv("disciplinas_ib.csv")

# Converte colunas de hora para datetime
def parse_hora(hora_str):
    return datetime.strptime(hora_str, "%H:%M").time()

df["inicio"] = df["inicio"].apply(parse_hora)
df["fim"] = df["fim"].apply(parse_hora)

# Timezone local
tz = pytz.timezone("America/Sao_Paulo")
agora = datetime.now(tz)
dia_semana = agora.strftime("%A")  # Monday, Tuesday...

# Mapeamento português -> inglês
mapa_dias = {
    "Segunda": "Monday",
    "Terça": "Tuesday",
    "Quarta": "Wednesday",
    "Quinta": "Thursday",
    "Sexta": "Friday",
    "Sábado": "Saturday",
}
dia_hoje = mapa_dias.get(df["dia"].iloc[0], dia_semana)  # fallback

# Filtrar disciplinas do dia atual
df_dia = df[df["dia"] == list(mapa_dias.keys())[list(mapa_dias.values()).index(dia_semana)]].copy()

# Converter para datetime de hoje
df_dia["inicio_dt"] = df_dia["inicio"].apply(lambda t: datetime.combine(agora.date(), t, tz))
df_dia["fim_dt"] = df_dia["fim"].apply(lambda t: datetime.combine(agora.date(), t, tz))

# Separar em andamento e futuras
andamento = df_dia[(df_dia["inicio_dt"] <= agora) & (df_dia["fim_dt"] > agora)].copy()
futuro = df_dia[df_dia["inicio_dt"] > agora].copy()

# Tempo restante em horas:min
def fmt_tempo(delta):
    h, m = divmod(int(delta.total_seconds() // 60), 60)
    return f"{h:02d}:{m:02d}"

andamento["status"] = andamento["fim_dt"].apply(lambda f: "⏳ " + fmt_tempo(f - agora) + " restantes")
futuro["status"] = futuro["inicio_dt"].apply(lambda i: "🕒 começa em " + fmt_tempo(i - agora))

# Ordenações
andamento = andamento.sort_values(["inicio_dt", "codigo"])
futuro = futuro.sort_values(["inicio_dt", "codigo"])

# ==============================
# Exibição no Streamlit
# ==============================
st.title("📚 Painel de Disciplinas - IB Unicamp")
st.write(f"⏰ Atualizado em: {agora.strftime('%H:%M')} ({dia_semana})")

if andamento.empty:
    st.info("Nenhuma disciplina em andamento no momento.")
else:
    st.subheader("📌 Disciplinas em andamento")
    st.table(
        andamento.reset_index(drop=True)[
            ["codigo", "nome", "turma", "inicio", "fim", "sala", "status"]
        ]
    )

if futuro.empty:
    st.info("Nenhuma próxima disciplina para hoje.")
else:
    st.subheader("⏭️ Próximas disciplinas")
    st.table(
        futuro.reset_index(drop=True)[
            ["codigo", "nome", "turma", "inicio", "fim", "sala", "status"]
        ]
    )
