import streamlit as st
import streamlit_authenticator as stauth
import os
from db import SessionLocal
from models_creed import Presos, Usuarios

with open('Paginas/Usuarios/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.set_page_config(layout='centered')
session = SessionLocal()


# -----Buscar Usuarios------
usuarios = session.query(Usuarios).all()
ids = [u.id for u in usuarios]
id_selecionado = st.selectbox('Usuário', ids,help='"🔍 Buscar por usuário"', placeholder='Digite o usuário.',format_func=lambda x: f'{x} - {next(p.username for p in usuarios if p.id==x)}')
usuario = session.query(Usuarios).filter(Usuarios.id==id_selecionado).first()

# UI da página
st.title("📋 Excluir Usuário")

if usuario:
    with st.form("form_excluir"):
        nome = st.text_input("Nome completo", disabled=True, value=usuario.nome)
        username = st.text_input("Usuário", placeholder='Digite sua matrícula sem o hifen.', disabled=True,value=usuario.username)
        enviar = st.form_submit_button("Excluir", key='danger')

        if enviar:
            try:
                session.delete(usuario)
                session.commit()
                st.success('Usuário deletado com sucesso!', icon='✅')
            except Exception as e:
                st.error(f'Não foi possível atualizar usuário: {e}')
            finally:
                session.close()
else:
    st.warning('Usuário não encontrado!')