import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Simulador Interativo de Secagem", layout="centered")
st.title("🧪 Simulador Interativo de Secagem de Granulado Farmacêutico")

# === GIF do leito fluidizado ===


# === Dados base e ruído como na sua planilha ===
dados_base = {
    40: [22, 19, 16, 14, 12, 11, 9, 8, 7, 6, 5],
    50: [22, 16, 13, 10, 7, 5, 4, 3, 2, 2, 1],
    60: [22, 11, 6, 3, 1, 0.8, 0.4, 0.4, 0.4, 0.4, 0.4]
}

ruidos = {
    40: [(0,0,1), (2,3,10), (8,9,10), (7,8,10), (8,9,10),
         (3,4,10), (8,9,10), (7,8,10), (6,7,100), (6,7,100), (8,9,10)],
    50: [(0,0,1), (8,9,10), (0,1,10), (0,1,100), (6,7,10),
         (8,9,10), (5,6,10), (4,5,10), (4,5,10), (0,1,10), (5,6,10)],
    60: [(0,0,1), (4,5,10), (0,1,10), (1,2,10), (6,7,10),
         (5,6,100), (4,5,100), (4,5,100), (4,5,100), (4,5,100), (4,5,100)]
}

tempos = np.arange(0, 5.5, 0.5)  # 0 a 5h, passo 0,5h

# === Sessão de estado do Streamlit para armazenar dados entre cliques ===
if "df_sim" not in st.session_state:
    st.session_state.df_sim = pd.DataFrame(columns=["Temperatura (°C)", "Tempo (h)", "Umidade (%)"])
    st.session_state.tempo_index = 0
    st.session_state.temp = None

# === Seleção de temperatura ===
temp = st.radio("Selecione a temperatura (°C):", [40, 50, 60])

# Reinicia o experimento se mudar a temperatura
if st.session_state.temp != temp:
    st.session_state.df_sim = pd.DataFrame(columns=["Temperatura (°C)", "Tempo (h)", "Umidade (%)"])
    st.session_state.tempo_index = 0
    st.session_state.temp = temp

# === Botão para registrar próximo ponto de tempo ===
if st.button("Registrar próximo tempo (+0,5 h)"):
    if st.session_state.tempo_index < len(tempos):
        base = dados_base[temp][st.session_state.tempo_index]
        min_r, max_r, div = ruidos[temp][st.session_state.tempo_index]
        if div == 1:
            umid = base
        else:
            umid = base + (np.random.randint(min_r, max_r + 1) + np.random.random()) / div
        # Adicionar linha à tabela
        nova_linha = pd.DataFrame({
            "Temperatura (°C)": [temp],
            "Tempo (h)": [tempos[st.session_state.tempo_index]],
            "Umidade (%)": [round(umid,3)]
        })
        st.session_state.df_sim = pd.concat([st.session_state.df_sim, nova_linha], ignore_index=True)
        st.session_state.tempo_index += 1
    else:
        st.warning("Todos os tempos já foram registrados!")

# Mostrar tabela atualizada
st.subheader("Dados coletados até agora")
st.dataframe(st.session_state.df_sim, hide_index=True)

# Botão para baixar CSV
if not st.session_state.df_sim.empty:
    st.download_button(
        label="⬇️ Baixar dados (CSV)",
        data=st.session_state.df_sim.to_csv(index=False).encode("utf-8"),
        file_name=f"secagem_{temp}C_experimento.csv",
        mime="text/csv"
    )