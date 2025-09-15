import pandas as pd
from datetime import datetime, timedelta
import pytz
import streamlit as st

# ====================================
# Configuração
# ====================================
tz = pytz.timezone("America/Sao_Paulo")

st.set_page_config(
    page_title="Painel de Disciplinas - IB Unicamp",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ====================================
# Funções auxiliares
# ====================================

def parse_time(hora_str, dia_semana):
    """Converte string de horário para datetime no timezone correto"""
    dias_map = {
        "Segunda": 0, "Terça": 1, "Quarta": 2,
        "Quinta": 3, "Sexta": 4, "Sábado": 5
    }
    hoje = datetime.now(tz)
    hora = datetime.strptime(hora_str, "%H:%M").time()
    dias_a_frente = (dias_map[dia_semana] - hoje.weekday()) % 7
    data_ref = (hoje + timedelta(days=dias_a_frente)).date()
    return tz.localize(datetime.combine(data_ref, hora))

def periodo(hora):
    """Classifica período do dia"""
    if hora < datetime.strptime("12:00", "%H:%M").time():
        return "🌅 Manhã"
    elif hora < datetime.strptime("18:00", "%H:%M").time():
        return "🌇 Tarde"
    else:
        return "🌙 Noite"

# ====================================
# Carregar dados
# ====================================
@st.cache_data
def carregar_dados():
    df = pd.read_csv("disciplinas_ib.csv")
    df["inicio_dt"] = df.apply(lambda x: parse_time(x["inicio"], x["dia"]), axis=1)
    df["fim_dt"] = df.apply(lambda x: parse_time(x["fim"], x["dia"]), axis=1)
    return df

df = carregar_dados()

# ====================================
# Painel
# ====================================
agora = datetime.now(tz)
map_pt = {
    "Monday": "Segunda", "Tuesday": "Terça", "Wednesday": "Quarta",
    "Thursday": "Quinta", "Friday": "Sexta", "Saturday": "Sábado"
}
hoje_pt = map_pt[agora.strftime("%A")]

st.title("📚 Painel de Disciplinas - IB Unicamp")
st.markdown(f"### 📅 {hoje_pt} | ⏰ {agora.strftime('%H:%M')}")

# Auto refresh a cada 1 minuto (60_000 ms)
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=60 * 1000, key="refresh")

# Filtrar somente disciplinas de hoje
df_hoje = df[df["dia"] == hoje_pt].copy()

# Em andamento
em_andamento = df_hoje[(df_hoje["inicio_dt"] <= agora) & (df_hoje["fim_dt"] > agora)].copy()
em_andamento["periodo"] = em_andamento["inicio_dt"].dt.time.apply(periodo)

# Próximas
proximas = df_hoje[df_hoje["inicio_dt"] > agora].copy().sort_values("inicio_dt")
proximas["periodo"] = proximas["inicio_dt"].dt.time.apply(periodo)

# Mostrar em andamento
if not em_andamento.empty:
    st.subheader("📌 Disciplinas em andamento")
    for periodo_nome, grupo in em_andamento.groupby("periodo"):
        st.markdown(f"#### {periodo_nome}")
        st.dataframe(
            grupo[["codigo", "nome", "turma", "inicio", "fim", "sala"]]
            .sort_values(["fim_dt", "codigo"])
            .reset_index(drop=True)
        )
else:
    st.info("Nenhuma disciplina em andamento.")

# Mostrar próximas
if not proximas.empty:
    st.subheader("⏭️ Próximas disciplinas")
    for periodo_nome, grupo in proximas.groupby("periodo"):
        st.markdown(f"#### {periodo_nome}")
        st.dataframe(
            grupo[["codigo", "nome", "turma", "inicio", "fim", "sala"]]
            .sort_values(["inicio_dt", "codigo"])
            .reset_index(drop=True)
        )
else:
    st.info("Nenhuma disciplina futura hoje.")

