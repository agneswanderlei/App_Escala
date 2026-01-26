import streamlit as st
from db import SessionLocal
from models import Eventos
import pandas as pd
import datetime

st.set_page_config(layout='centered')
session = SessionLocal()

st.title("📋 Visualizar Eventos")

igreja_id = st.session_state.get("igreja")
perfil = st.session_state.get("perfil")

# --- Data de hoje ---
hoje = datetime.date.today()

# --- Buscar eventos conforme perfil, apenas futuros ---
if perfil == 'Supervisor':
    eventos = session.query(Eventos).order_by(Eventos.data.asc()).all()
else:
    eventos = session.query(Eventos).filter_by(igreja_id=igreja_id).order_by(Eventos.data.asc()).all()

if not eventos:
    st.warning("Nenhum evento encontrado.")
    st.stop()

# --- Filtros ---
with st.expander("Filtros"):
    nome_filtro = st.text_input("Filtrar por nome do evento:")
    with st.container(horizontal=True):
        data_inicial = st.date_input("Data Inicial:", value=hoje, format="DD/MM/YYYY")
        data_final = st.date_input("Data Final:", value=None, format="DD/MM/YYYY")

    if nome_filtro:
        eventos = [e for e in eventos if nome_filtro.lower() in e.nome.lower()]
    # Filtro por data inicial/final
    if data_inicial and data_final:
        eventos = [e for e in eventos if data_inicial <= e.data <= data_final]
    elif data_inicial:
        eventos = [e for e in eventos if e.data >= data_inicial]
    elif data_final:
        eventos = [e for e in eventos if e.data <= data_final]

    if not eventos:
        st.warning("Nenhum evento encontrado com os filtros aplicados.")
        st.stop()

# --- Escolher visualização ---
modo = st.radio("Modo de visualização:", ["Tabela", "Expanders"], horizontal=True)

if modo == "Tabela":
    dados = []
    for e in eventos:
        dados.append({
            "Nome": e.nome,
            "Data": e.data.strftime('%d/%m/%Y'),
            "Hora": e.hora.strftime('%H:%M') if e.hora else "Não especificada",
            "Descrição": e.descricao or "Nenhuma descrição fornecida."
        })
    st.dataframe(pd.DataFrame(dados))

else:  # Expanders
    for e in eventos:
        with st.expander(f"📌 {e.nome} — {e.data.strftime('%d/%m/%Y')}"):
            st.write(f"**Nome:** {e.nome}")
            st.write(f"**Data:** {e.data.strftime('%d/%m/%Y')}")
            st.write(f"**Hora:** {e.hora.strftime('%H:%M') if e.hora else 'Não especificada'}")
            
            st.markdown("### 👥 Escalados")
            st.write("- Em breve será implementado -")
            
            st.markdown("### 📖 Liturgia")
            st.write("- Em breve será implementado -")
            
            st.markdown("### 📝 Descrição")
            st.write(e.descricao or "Nenhuma descrição fornecida.")

session.close()