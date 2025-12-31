import streamlit as st
from db import SessionLocal
from models import Funcoes, Usuarios

st.set_page_config(layout='centered')
session = SessionLocal()

st.title("🏛️ Lista de Funções")

# Buscar todas as função cadastradas
igreja_id = st.session_state.get("igreja")
funcoes = session.query(Funcoes).filter_by(igreja_id=igreja_id).all()

if not funcoes:
    st.warning("Nenhuma função cadastrada ainda.")
else:
    # Exibir em tabela
    dados = [{"ID": funcao.id, "Nome": funcao.nome, "Descrição": funcao.descricao} for funcao in funcoes]
    st.dataframe(dados)

session.close()