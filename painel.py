import pandas as pd
import streamlit as st
from datetime import datetime
import pytz
import time

# ===============================
# Configurações
# ===============================
TZ = pytz.timezone("America/Sao_Paulo")

# Lê os dados fixos (não precisa reler a cada refresh)
df_base = pd.read_csv("disciplinas_ib.csv")
df_base["inicio"] = pd.to_datetime(df_base["inicio"], format="%H:%M").dt.time
df_base["fim"] = pd.to_datetime(df_base["fim"], format="%H:%M").dt.time

# UI fixa
st.set_page_config(layout="wide")
st.title("📚 Painel de Disciplinas - IB Unicamp")

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


def tempo_formatado(delta):
    total_min = int(round(delta.total_seconds() / 60))
    h, m = divmod(total_min, 60)
    return f"{h:02d}h {m:02d}m"


def classificar(row, agora):
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


def df_to_styled_html(df, tempo_col):
    df = df.rename(columns={"tempo": tempo_col})
    df = df[["codigo", "sala", "turma", "nome", "inicio", "fim", tempo_col]]
    html = df.to_html(index=False, escape=False)

    for col in ["codigo", "sala", "turma", "inicio", "fim"]:
        for val in df[col].astype(str).unique():
            html = html.replace(f'<td>{val}', f'<td class="mono">{val}')
    return html


# Bloco dinâmico que será atualizado
placeholder = st.empty()

while True:
    agora = datetime.now(TZ)
    dia_semana = agora.strftime("%A")
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

    # Filtra disciplinas do dia
    df = df_base[df_base["dia"] == hoje].copy()
    df["inicio_dt"] = df["inicio"].apply(lambda t: TZ.localize(datetime.combine(agora.date(), t)))
    df["fim_dt"] = df["fim"].apply(lambda t: TZ.localize(datetime.combine(agora.date(), t)))

    df["status"] = df.apply(lambda r: classificar(r, agora), axis=1)
    df["periodo"] = df.apply(periodo, axis=1)

    def info_tempo(row):
        if row["status"] == "andamento":
            return tempo_formatado(row["fim_dt"] - agora)
        elif row["status"] == "proxima":
            return tempo_formatado(row["inicio_dt"] - agora)
        return None

    df["tempo"] = df.apply(info_tempo, axis=1)
    df["inicio"] = df["inicio"].apply(lambda t: t.strftime("%H:%M"))
    df["fim"] = df["fim"].apply(lambda t: t.strftime("%H:%M"))

    # Reescreve só esta parte
    with placeholder.container():
        st.markdown(f"### 📅 Hoje: **{hoje}** | ⏰ Agora: {agora.strftime('%H:%M')}")

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

    # Espera 60 segundos e atualiza só este bloco
    time.sleep(60)
