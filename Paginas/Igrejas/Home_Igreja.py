import streamlit as st
from db import SessionLocal
from models import Igrejas

st.set_page_config(layout='centered')
session = SessionLocal()

st.title("🏛️ Lista de Igrejas")

# Buscar todas as igrejas cadastradas
igrejas = session.query(Igrejas).all()

if not igrejas:
    st.warning("Nenhuma igreja cadastrada ainda.")
else:
    # Exibir em tabela
    dados = [{"ID": igreja.id, "Nome": igreja.nome} for igreja in igrejas]
    st.dataframe(dados)

session.close()