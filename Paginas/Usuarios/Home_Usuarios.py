import streamlit as st
import streamlit_authenticator as stauth
import os
from db import SessionLocal
from models_creed import Presos, Usuarios
import pandas as pd
st.set_page_config(layout='centered')
session = SessionLocal()

usuarios = session.query(Usuarios).all()


# Formulario
st.subheader('Lista dos Usuários 📋')
col1, col2, col3 = st.columns(3)
with col1:
    usuario_nome = st.multiselect('Nome', options=[u.nome for u in usuarios])
with col2:
    usuario = st.multiselect('Usuário', options=[u.username for u in usuarios])
with col3:
    perfil = st.multiselect('Perfil', options=[u.perfil for u in usuarios])

# FILTROS
# Corrigido: criar lista de dicionários para o DataFrame
usuarios_dict = [{'nome': u.nome, 'username': u.username, 'perfil': u.perfil} for u in usuarios]
df_usuarios = pd.DataFrame(usuarios_dict)
if usuario_nome:
    df_usuarios = df_usuarios[df_usuarios['nome'].isin(usuario_nome)]
if usuario:
    df_usuarios = df_usuarios[df_usuarios['username'].isin(usuario)]
if perfil:
    df_usuarios = df_usuarios[df_usuarios['perfil'].isin(perfil)]

# ALTERAR OS NOMES DAS COLUNAS DO DF
df_usuarios = df_usuarios.rename(
    columns={
        'nome': 'Nome',
        'username': 'Usuário',
        'perfil': 'Perfil',
    }
)

# DATAFRAME
st.dataframe(df_usuarios[['Nome','Usuário', 'Perfil']])

