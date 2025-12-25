import streamlit as st
import streamlit_authenticator as stauth
import os
from db import SessionLocal
from models import Usuarios

with open('Paginas/Usuarios/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
st.set_page_config(layout='centered')
session = SessionLocal()
# UI da página
st.title("📋 Cadastro de Usuário")

with st.form("form_cadastro"):
    nome = st.text_input("Nome completo")
    username = st.text_input("Usuário", placeholder='Digite seu CPF')
    perfil = st.selectbox('Perfil',options=['Admin','Gerente','Operador'],index=None)
    senha = st.text_input("Senha", type="password")
    confirmar = st.text_input("Confirmar senha", type="password")
    enviar = st.form_submit_button("Cadastrar", key='success')

    if enviar:
        if senha != confirmar:
            st.warning("🔁 As senhas não coincidem.")
        elif not nome or not username or not senha:
            st.warning("📌 Todos os campos são obrigatórios.")
        else:
            try:
                senha_hash = stauth.Hasher.hash(senha)
                username = username.replace('-', '').strip()
                novo_usuario = Usuarios(
                    nome=nome,
                    cpf=username,
                    perfil=perfil,
                    password=senha_hash
                )
                session.add(novo_usuario)
                session.commit()
                st.success('Usuário cadastrado com sucesso!',icon='✅')
            except Exception as e:
                session.rollback()
                st.error(f'Não foi possível adicionar usuario: {e}')
            finally:
                session.close()