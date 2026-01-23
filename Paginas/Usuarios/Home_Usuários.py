import streamlit as st
from db import SessionLocal
from models import Usuarios, Ministerios
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

    with st.expander('Filtros'):
        with st.container(horizontal=True):
            
            # Buscar todas as igrejas dos usuários
            igrejas = [u.igreja.nome for u in usuarios if u.igreja]

            # Remover duplicados mantendo a ordem
            igrejas_unicas = list(dict.fromkeys(igrejas))

            igreja_filtro = st.multiselect(
                "Igreja",
                options=igrejas_unicas,
                placeholder='Escolha a Igreja'
            )
            usuario_nome = st.multiselect('Nome', options=[u.nome for u in usuarios], placeholder='Escolha o nome')
            usuario = st.multiselect('Usuário', options=[u.cpf for u in usuarios], placeholder='Escolha o CPF')
        with st.container(horizontal=True):
            perfil = st.multiselect('Perfil', options=set([u.perfil for u in usuarios]), placeholder='Escolha o perfil')
            ministerios_all = session.query(Ministerios).filter_by(igreja_id=igreja_logada)
            ministerios = st.multiselect(
                'Ministérios',
                options=[m.nome for m in ministerios_all],
                placeholder='Escolha os ministérios'
            )

        

    # Criar lista de dicionários para DataFrame (incluindo igreja)
    usuarios_dict = [
        {
            'nome': u.nome,
            'cpf': u.cpf,
            'perfil': u.perfil,
            'igreja': u.igreja.nome if u.igreja else "-",
            'ministerios': ', '.join([m.nome for m in u.ministerios] or '-')
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
    if ministerios:
        df_usuarios = df_usuarios[df_usuarios['ministerios'].apply(lambda x: any(m in x for m in ministerios))]

    # Renomear colunas
    df_usuarios = df_usuarios.rename(
        columns={
            'nome': 'Nome',
            'cpf': 'CPF',
            'perfil': 'Perfil',
            'igreja': 'Igreja',
            'ministerios': 'Ministérios'
        }
    )

    # Mostrar tabela
    st.dataframe(df_usuarios[['Nome', 'CPF', 'Perfil', 'Igreja', 'Ministérios']])