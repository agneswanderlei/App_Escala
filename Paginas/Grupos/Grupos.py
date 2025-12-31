import streamlit as st
from db import SessionLocal
from models import Ministerios, Usuarios

st.set_page_config(layout='centered')
session = SessionLocal()

st.title("🏛️ Lista de Grupos")

# Buscar todos os grupos cadastrados
igreja_id = st.session_state.get("igreja")
grupos = session.query(Ministerios).filter_by(igreja_id=igreja_id).all()

if not grupos:
    st.warning("Nenhum grupo cadastrado ainda.")
else:
    # Exibir em tabela
    dados = [{"ID": grupo.id, "Nome": grupo.nome} for grupo in grupos]
    st.dataframe(dados)

session.close()