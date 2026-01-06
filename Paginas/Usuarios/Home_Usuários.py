import streamlit as st
import os
import streamlit_authenticator as stauth
from db import SessionLocal
from models import Usuarios, Igrejas
import pandas as pd

st.set_page_config(layout='centered')
session = SessionLocal()

# ----- Buscar usuários conforme perfil -----
perfil_logado = st.session_state.get("perfil")
igreja_logada = st.session_state.get("igreja")

if perfil_logado == "Supervisor":
    usuarios = session.query(Usuarios).all()
elif perfil_logado == "Administrador":
    usuarios = session.query(Usuarios).filter_by(igreja_id=igreja_logada).all()
else:
    st.warning("⚠️ Você não tem permissão para visualizar a lista de usuários.")
    usuarios = []

# Só mostra a tabela se houver usuários
if usuarios:
    st.subheader('Lista dos Usuários 📋')

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        usuario_nome = st.multiselect('Nome', options=[u.nome for u in usuarios])
    with col2:
        usuario = st.multiselect('Usuário', options=[u.cpf for u in usuarios])
    with col3:
        perfil = st.multiselect('Perfil', options=[u.perfil for u in usuarios])
    with col4:
        igreja_filtro = st.multiselect('Igreja', options=[u.igreja.nome for u in usuarios])

    # Criar lista de dicionários para DataFrame (incluindo igreja)
    usuarios_dict = [
        {
            'nome': u.nome,
            'cpf': u.cpf,
            'perfil': u.perfil,
            'igreja': u.igreja.nome if u.igreja else "-"
        }
        for u in usuarios
    ]
    df_usuarios = pd.DataFrame(usuarios_dict)

    # Aplicar filtros
    if usuario_nome:
        df_usuarios = df_usuarios[df_usuarios['nome'].isin(usuario_nome)]
    if usuario:
        df_usuarios = df_usuarios[df_usuarios['cpf'].isin(usuario)]
    if perfil:
        df_usuarios = df_usuarios[df_usuarios['perfil'].isin(perfil)]
    if igreja_filtro:
        df_usuarios = df_usuarios[df_usuarios['igreja'].isin(igreja_filtro)]

    # Renomear colunas
    df_usuarios = df_usuarios.rename(
        columns={
            'nome': 'Nome',
            'cpf': 'Usuário',
            'perfil': 'Perfil',
            'igreja': 'Igreja'
        }
    )

    # Mostrar tabela
    st.dataframe(df_usuarios[['Nome', 'Usuário', 'Perfil', 'Igreja']])