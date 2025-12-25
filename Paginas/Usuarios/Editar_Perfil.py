import streamlit as st
import streamlit_authenticator as stauth
import os
from db import SessionLocal
from models import Usuarios

with open('Paginas/Usuarios/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
st.set_page_config(layout='centered')
session = SessionLocal()



# -----Buscar Usuarios------
usuarios = session.query(Usuarios).all()
ids = [u.id for u in usuarios]
id_selecionado = st.selectbox('Usuário', ids, help='"🔍 Buscar Usuário"', placeholder='Digite o usuário.',format_func=lambda x: f'{x} - {next(p.cpf for p in usuarios if p.id==x)}')
usuario = session.query(Usuarios).filter(Usuarios.id==id_selecionado).first()
# UI da página
st.title("📋 Editar Perfil")

if usuario:
    with st.form("form_perfil"):
        nome = st.text_input("Nome completo", disabled=True, value=usuario.nome)
        username = st.text_input("Usuário", placeholder='Digite seu usuário.', disabled=True,value=usuario.cpf)
        perfil = st.selectbox('Perfil',options=['Administrador','Líder', 'Auxiliar'],index=['Administrador','Líder', 'Auxiliar'].index(usuario.perfil))
        enviar = st.form_submit_button("Atualizar", key='warning')

        if enviar:
            try:
                usuario.perfil = perfil
                session.commit()
                st.success('Usuario atualizado com sucesso!')
            except Exception as e:
                session.rollback()
                st.error(f'Erro ao atualizar usuário: {e}')
            finally:
                session.close()
else:
    st.warning('Usuário não encontrado!')