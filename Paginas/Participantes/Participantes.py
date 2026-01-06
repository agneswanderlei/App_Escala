import streamlit as st
from db import SessionLocal
from models import Participantes, Ministerios, Funcoes

st.set_page_config(layout='centered')
session = SessionLocal()

st.title("🏛️ Lista de Participantes")

igreja_id = st.session_state.get("igreja")

# Buscar todos os participantes da igreja
participantes = session.query(Participantes).filter_by(igreja_id=igreja_id).all()

if not participantes:
    st.warning("Nenhum participante cadastrado ainda.")
else:
    # Buscar ministérios e funções da igreja
    ministerios = session.query(Ministerios).filter_by(igreja_id=igreja_id).all()
    funcoes = session.query(Funcoes).filter_by(igreja_id=igreja_id).all()

    # --- Filtros ---
    with st.expander("🔎 Filtros"):
        filtro_nome = st.text_input("Filtrar por nome")
        filtro_ministerios = st.multiselect(
            "Filtrar por ministérios",
            options=[m.nome for m in ministerios]
        )
        filtro_funcoes = st.multiselect(
            "Filtrar por funções",
            options=[f.nome for f in funcoes]
        )

    # --- Aplicar filtros ---
    participantes_filtrados = participantes

    if filtro_nome:
        participantes_filtrados = [p for p in participantes_filtrados if filtro_nome.lower() in p.nome.lower()]

    if filtro_ministerios:
        participantes_filtrados = [
            p for p in participantes_filtrados
            if any(m.nome in filtro_ministerios for m in p.ministerios)
        ]

    if filtro_funcoes:
        participantes_filtrados = [
            p for p in participantes_filtrados
            if any(f.nome in filtro_funcoes for f in p.funcoes)
        ]

    # --- Montar dados para tabela ---
    dados = []
    for p in participantes_filtrados:
        dados.append({
            "ID": p.id,
            "Nome": p.nome,
            "Telefone": p.telefone or "",
            "Ministérios": ", ".join([m.nome for m in p.ministerios]) or "-",
            "Funções": ", ".join([f.nome for f in p.funcoes]) or "-"
        })

    st.dataframe(dados)

session.close()