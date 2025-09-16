import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import pytz

# ==============================
# Configuração
# ==============================
st.set_page_config(page_title="📚 Painel de Disciplinas", layout="centered")

# Carrega planilha
df = pd.read_csv("disciplinas_ib.csv")

# Converte colunas de hora
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
dia_portugues = [k for k, v in mapa_dias.items() if v == dia_semana][0]

# Filtrar disciplinas do dia atual
df_dia = df[df["dia"] == dia_portugues].copy()

# Função para combinar hora com timezone correto
def combinar_com_tz(hora, agora, tz):
    dt = datetime.combine(agora.date(), hora)  # datetime naive
    return tz.localize(dt)  # aplica timezone

df_dia["inicio_dt"] = df_dia["inicio"].apply(lambda t: combinar_com_tz(t, agora, tz))
df_dia["fim_dt"] = df_dia["fim"].apply(lambda t: combinar_com_tz(t, agora, tz))

# Separar em andamento e futuras (descartando as já encerradas)
andamento = df_dia[(df_dia["inicio_dt"] <= agora) & (df_dia["fim_dt"] > agora)].copy()
futuro = df_dia[df_dia["inicio_dt"] > agora].copy()

# Função formatadora de tempo
def fmt_tempo(delta):
    h, m = divmod(int(delta.total_seconds() // 60), 60)
    return f"{h:02d}:{m:02d}"

# Colunas de status
andamento["status"] = andamento["fim_dt"].apply(lambda f: "⏳ " + fmt_tempo(f - agora) + " restantes")
futuro["status"] = futuro["inicio_dt"].apply(lambda i: "🕒 começa em " + fmt_tempo(i - agora))

# Ordenações
andamento = andamento.sort_values(["inicio_dt", "codigo"])
futuro = futuro.sort_values(["inicio_dt", "codigo"])

# Classificação por período
def classificar_periodo(hora):
    if hora < datetime.strptime("12:00", "%H:%M").time():
        return "🌅 Manhã"
    elif hora < datetime.strptime("18:00", "%H:%M").time():
        return "🌇 Tarde"
    else:
        return "🌙 Noite"

andamento["período"] = andamento["inicio"].apply(classificar_periodo)
futuro["período"] = futuro["inicio"].apply(classificar_periodo)

# ==============================
# Exibição no Streamlit
# ==============================
st.title("📚 Painel de Disciplinas - IB Unicamp")
st.write(f"⏰ Atualizado em: {agora.strftime('%H:%M')} ({dia_portugues})")

if andamento.empty:
    st.info("Nenhuma disciplina em andamento no momento.")
else:
    st.subheader("📌 Disciplinas em andamento")
    for periodo, grupo in andamento.groupby("período"):
        st.markdown(f"### {periodo}")
        st.dataframe(
            grupo[["codigo", "nome", "turma", "inicio", "fim", "sala", "status"]],
            hide_index=True,
            use_container_width=True
        )

if futuro.empty:
    st.info("Nenhuma próxima disciplina para hoje.")
else:
    st.subheader("⏭️ Próximas disciplinas")
    for periodo, grupo in futuro.groupby("período"):
        st.markdown(f"### {periodo}")
        st.dataframe(
            grupo[["codigo", "nome", "turma", "inicio", "fim", "sala", "status"]],
            hide_index=True,
            use_container_width=True
        )

